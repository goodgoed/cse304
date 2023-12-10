from decaf_visitor import NodeVisitor
from decaf_ast import Type_Record, ASTNode, SkipStmt
import pdb, sys

class TypeChecker(NodeVisitor):
    def __init__(self, symbolTable):
        super().__init__()
        self.s = symbolTable
        self.current_class = None
        self.current_method_id = None

    def isSubtype(self, type1, type2):
        # Type T is a subtype of itself
        if type1.equals(type2):
            return True
        # int is a subtype of float
        elif type1.equals('int') and type2.equals('float'):
            return True
        # user(A) is a subtype of user(B) if A is a subclass of B
        elif type1.isUserDefined() and type2.isUserDefined():
            type1_obj = type1.type_obj
            type2_obj = type2.type_obj
            current_class = self.s.lookup_class(type1_obj)

            super_class = self.s.lookup_class(current_class['super_class'])
            while super_class:
                if super_class.name == type2_obj:
                    return True
            return False
        # null is a subtype of user(A) for any class A
        elif type1.isNull() and type2.isUserDefined():
            return True
        # class-literal(A) is a subtype of class-literal(B) if A is a subclass of B
        elif type1.isClassLiteral() and type2.isClassLiteral():
            type1_obj = type1.type_obj
            type2_obj = type2.type_obj
            current_class = self.s.lookup_class(type1_obj)
            super_class = self.s.lookup_class(current_class.super)
            while super_class:
                if super_class.name == type2_obj:
                    return True
            return False
        else:
            return False

    def visit_Program(self, node, context):
        for _class in node.result:
            _class.accept(self)

    def visit_Class_Record(self, node, context):
        self.current_class = node.name
        for constructor in node.constructors:
            constructor.accept(self)
        for method in node.methods:
            method.accept(self)
        for field in node.fields:
            field.accept(self)
        self.current_class = None

    def visit_Constructor_Record(self, node, context):
        node.body.accept(self)

    def visit_Method_Record(self, node, context):
        self.current_method_id = node.id
        node.body.accept(self)
        self.current_method_id = None

    def visit_VarDeclStmt(self, node, context):
        node.type_correct = True

    def visit_IfStmt(self, node, context):
        node.condition.accept(self)
        node.then_stmt.accept(self)
        node.else_stmt.accept(self)

        condition_type = node.condition.type
        then_stmt_type_correct = node.then_stmt.type_correct
        else_stmt_type_correct = node.else_stmt.type_correct

        if condition_type.isBoolean() and then_stmt_type_correct and else_stmt_type_correct:
            node.type_correct = True
        else:
            print(f"ERROR [{node.start}:{node.end}]: Condition must be boolean in the If Statement")
            exit(1)

        # print(f"DEBUG: {type(node).__name__} type_correct -> {node.type_correct}", file=sys.stderr)

    def visit_WhileStmt(self, node, context):
        node.condition.accept(self)
        node.body.accept(self)
        
        condition_type = node.condition.type
        body_type_correct = node.body.type_correct

        if not condition_type.isError() and condition_type.isBoolean() and body_type_correct:
            node.type_correct = True
        else:
            print(f"ERROR [{node.start}:{node.end}]: Condition must be boolean in the While Statement")
            exit(1)

        # print(f"DEBUG: {type(node).__name__} type_correct -> {node.type_correct}", file=sys.stderr)

    def visit_ForStmt(self, node, context):
        node.initializer.accept(self)
        node.condition.accept(self)
        node.update.accept(self)
        node.body.accept(self)

        initializer_type_correct = node.initializer.type_correct
        condition_type_check = node.condition.type_correct if isinstance(node.condition, SkipStmt) else node.condition.type.isBoolean()
        update_type_correct = node.update.type_correct
        body_type_correct = node.body.type_correct

        if condition_type_check and initializer_type_correct and update_type_correct and body_type_correct:
            node.type_correct = True
        else:
            print(f"ERROR [{node.start}:{node.end}]: Condition must be boolean in the For Statement")
            exit(1)
        
        # # print(f"DEBUG: {type(node).__name__} type_correct -> {node.type_correct}", file=sys.stderr)

    def visit_ReturnStmt(self, node, context):
        method_record = self.s.lookup_method(self.current_method_id)
        return_type = method_record.return_type
        
        #Check for empty expr
        if node.expr == '' and return_type.isVoid():
            node.type_correct = True
        elif isinstance(node.expr, ASTNode):
            node.expr.accept(self)
            
            expr_type = node.expr.type

            if not expr_type.isError() and self.isSubtype(expr_type, return_type):
                node.type_correct = True
            else:
                print(f"ERROR [{node.start}:{node.end}]: Return type did not match")
                exit(1)
        else:
            print(f"ERROR [{node.start}:{node.end}]: Return type did not match")
            exit(1) 

        # print(f"DEBUG: {type(node).__name__} type_correct -> {node.type_correct}", file=sys.stderr)

    def visit_ExprStmt(self, node, context):
        node.expr.accept(self)
        expr_type = node.expr.type
        if not expr_type.isError():
            node.type_correct = True
        else:
            node.type_correct = False
        
        # print(f"DEBUG: {type(node).__name__} type_correct -> {node.type_correct}", file=sys.stderr)

    def visit_BlockStmt(self, node, context):
        node.type_correct = True
        for stmt in node.stmt_list:
            stmt.accept(self)
            if hasattr(stmt, 'type_correct') and not stmt.type_correct:
                node.type_correct = False

        # print(f"DEBUG: {type(node).__name__} type_correct -> {node.type_correct}", file=sys.stderr)

    def visit_BreakStmt(self, node, context):
        node.type_correct = True

    def visit_ContinueStmt(self, node, context):
        node.type_correct = True

    def visit_SkipStmt(self, node, context):
        node.type_correct = True

    def visit_ConstantExpr(self, node, context):
        if node.constant_type == "integer":
            node.type = Type_Record('int')
        elif node.constant_type == "float":
            node.type = Type_Record('float')
        elif node.constant_type == "string":
            node.type = Type_Record('string')
        elif node.constant_type == "null":
            node.type = Type_Record('null')
        elif node.constant_type == "true" or node.constant_type == "false":
            node.type = Type_Record('boolean')

    def visit_VarExpr(self, node, context):
        node.type = node.record.type
        # print(f"DEBUG: {type(node).__name__} {node.variable_name} type -> {node.type}", file=sys.stderr)

    def visit_UnaryExpr(self, node, context):
        node.operand.accept(self)

        operator = node.operator
        operand_type = node.operand.type
        if (operator == 'uminus' and operand_type.isNumeric()) or operator == 'plus':
            node.type = operand_type.copy()
        elif operator == 'neg' and operand_type.isBoolean():
            node.type = operand_type.copy()
        else:
            print(f"ERROR [{node.start}:{node.end}]: Unary operator ({node.operator}) is not allowed for {operand_type}")
            exit(1)

        # print(f"DEBUG: {type(node).__name__} type -> {node.type}", file=sys.stderr)

    def visit_BinaryExpr(self, node, context):
        node.left_operand.accept(self)
        node.right_operand.accept(self)

        left_type = node.left_operand.type
        right_type = node.right_operand.type

        if node.operator in ('add', 'sub', 'mul', 'div'):
            # Check whether type of both operands is either 'int' or 'float'
            if not left_type.isNumeric() or not right_type.isNumeric():
                print(f"ERROR [{node.start}:{node.end}]: Binary operator ({node.operator}) is only allowed between numbers")
                exit(1)
            else:
                # If they have the same type, the type of the expression is one of their type
                if left_type.equals(right_type):
                    node.type = left_type.copy()
                # If they have different type, then type is 'float'
                else:
                    node.type = Type_Record('float')
        elif node.operator in ('and', 'or'):
            if not left_type.isBoolean() or not right_type.isBoolean():
                print(f"ERROR [{node.start}:{node.end}]: Binary operator ({node.operator}) is only allowed between boolean values")
                exit(1)
            else:
                node.type = Type_Record('boolean')
        elif node.operator in ('lt', 'leq', 'gt', 'geq'):
            # Check whether type of both operands is either 'int' or 'float'
            if not left_type.isNumeric() or not right_type.isNumeric():
                print(f"ERROR [{node.start}:{node.end}]: Binary operator ({node.operator}) is only allowed between numbers")
                exit(1)
            else:
                node.type = Type_Record('boolean')
        elif node.operator in ('eq', 'neq'):
            if not self.isSubtype(left_type, right_type) and not self.isSubtype(right_type, left_type):
                print(f"ERROR [{node.start}:{node.end}]: {left_type} and {right_type} cannot be compared")
                exit(1)
            else:
                node.type = Type_Record('boolean')
        
        # print(f"DEBUG: {type(node).__name__} type -> {node.type}", file=sys.stderr)

    def visit_AssignExpr(self, node, context):
        node.left_operand.accept(self)
        node.right_operand.accept(self)

        left_type = node.left_operand.type
        right_type = node.right_operand.type

        if not left_type.isError() and not right_type.isError() and self.isSubtype(right_type, left_type):
            node.type = left_type.copy()
            node.left_type = left_type
            node.right_type = right_type
        else:
            print(f"ERROR [{node.start}:{node.end}]: {right_type} cannot be assigned to {left_type}")
            exit(1)

        # print(f"DEBUG: {type(node).__name__} type -> {node.type}", file=sys.stderr)

    def visit_AutoExpr(self, node, context):
        node.operand.accept(self)

        operand_type = node.operand.type
        if operand_type.isNumeric():
            node.type = operand_type.copy()
        else:
            print(f"ERROR [{node.start}:{node.end}]: Automatic expression is only allowed for numbers")
            exit(1)

        # print(f"DEBUG: {type(node).__name__} type -> {node.type}", file=sys.stderr)

    def visit_FieldAccessExpr(self, node, context):
        node.base.accept(self)

        base_type = node.base.type
        base_class = base_type.type_obj
        field_name = node.field_name

        field_record = self.s.lookup_field(field_name,self.s.lookup_class(base_type.type_obj))

        if field_record == None:
            print(f"ERROR [{node.start}:{node.end}]: Field ({field_name}) was not defined")
            exit(1)

        field_id = field_record.id
        field_type = field_record.type
        field_containing_class = field_record.containing_class
        field_visibility = field_record.visibility
        field_applicability = field_record.applicability

        is_accessible = field_visibility == 'public' or (field_visibility == 'private' and self.current_class == field_containing_class)

        if base_type.isUserDefined():
            if (field_applicability == 'instance' or field_applicability == 'static') and is_accessible:
                node.type = field_type.copy()
                node.id = field_id
            else:
                print(f"ERROR [{node.start}:{node.end}]: Field ({field_name}) could not be accessed")
                exit(1)
        elif base_type.isClassLiteral():
            if field_applicability == 'static' and is_accessible:
                node.type = field_type.copy()
                node.id = field_id
            else:
                print(f"ERROR [{node.start}:{node.end}]: Field ({field_name}) could not be accessed")
                exit(1)


        # print(f"DEBUG: {type(node).__name__} type -> {node.type}", file=sys.stderr)
    
    def visit_MethodCallExpr(self, node, context):
        node.base.accept(self)
        for arg in node.arguments:
            arg.accept(self)
        base_type = node.base.type
        base_class = base_type.type_obj
        method_name = node.method_name
        arguments = node.arguments

        method_record = self.s.lookup_method_by_name(base_class, method_name)

        if method_record is None:
            print(f"ERROR [{node.start}:{node.end}]: Method ({method_name}) was not defined")
            exit(1)
        
        node.id = method_record.id
        method_record_containing_class = method_record.containing_class
        method_record_visibility = method_record.visibility
        method_record_applicability = method_record.applicability
        method_record_parameters = method_record.parameters
        method_record_return_type = method_record.return_type

        is_accessible = method_record_visibility == 'public' or (method_record_visibility == 'private' and self.current_class == method_record_containing_class)

        if base_type.isUserDefined():
            if method_record_applicability == 'instance' and is_accessible:
                if len(method_record_parameters) == len(arguments):
                    node.type = method_record_return_type.copy()
                else:
                    print(f"ERROR [{node.start}:{node.end}]: Number of arguments for the Method ({method_name}) was not eqaul")
                    exit(1)
                
                for param, arg in zip(method_record_parameters, arguments):
                    if not self.isSubtype(arg.type, param.type):
                        print(f"ERROR [{node.start}:{node.end}]: Argument type for the Method ({method_name}) was not right")
                        exit(1)
            else:
                print(f"ERROR [{node.start}:{node.end}]: Method ({method_name}) could not be accessed")
                exit(1)
        elif base_type.isClassLiteral():
            if method_record_applicability == 'static' and is_accessible:
                if len(method_record_parameters) == len(arguments):
                    node.type = method_record_return_type.copy()
                else:
                    print(f"ERROR [{node.start}:{node.end}]: Number of arguments for the Method ({method_name}) was not eqaul")
                    exit(1)

                for param, arg in zip(method_record_parameters, arguments):
                    if not self.isSubtype(arg.type, param.type):
                        print(f"ERROR [{node.start}:{node.end}]: Argument type for the Method ({method_name}) was not right")
                        exit(1)
            else:
                print(f"ERROR [{node.start}:{node.end}]: Method ({method_name}) could not be accessed")
                exit(1)

        # print(f"DEBUG: {type(node).__name__} type -> {node.type}", file=sys.stderr)

    def visit_NewObjectExpr(self, node, context):
        class_name = node.class_name
        for arg in node.constructor_args:
            arg.accept(self)
        arguments = node.constructor_args
        class_record = self.s.lookup_class(class_name)

        if class_record:
            node.type = Type_Record(class_name)
        else:
            print(f"ERROR [{node.start}:{node.end}]: Class ({class_name}) was not defined")
            exit(1)
        

        constructor_record = class_record['constructors']
        if len(constructor_record) == 0:
            print(f"ERROR [{node.start}:{node.end}]: No constructor was defined for the Class ({class_name})")
            exit(1)
        else:
            constructor_record = constructor_record[0]

        node.id = constructor_record.id
        constructor_parameters = constructor_record.parameters
        constructor_visibility = constructor_record.visibility

        if len(constructor_parameters) == len(arguments):
            node.type = Type_Record(class_name)
        else:
            print(f"ERROR [{node.start}:{node.end}]: Number of arguments for the Constructor ({class_name}) was not eqaul")
            exit(1)
        
        if constructor_visibility == 'private' and self.current_class != class_name:
            print(f"ERROR [{node.start}:{node.end}]: Constructor ({class_name}) could not be accessed")
            exit(1)

        for param, arg in zip(constructor_parameters, arguments):
            if not self.isSubtype(arg.type, param.type):
                print(f"ERROR [{node.start}:{node.end}]: Argument type for the Constructor ({class_name}) was not right")
                exit(1)

        # print(f"DEBUG: {type(node).__name__} type -> {node.type}", file=sys.stderr)

    def visit_ThisExpr(self, node, context):
        node.type = Type_Record(self.current_class)

    def visit_SuperExpr(self, node, context):
        current_class_record = self.s.lookup_class(self.current_class)
        super_class_record = self.s.lookup_class(current_class_record['super_class'])

        if super_class_record:
            node.type = Type_Record(super_class_record.name)
        else:
            print(f"ERROR [{node.start}:{node.end}]: Class {current_class_record['name']} has no super class")
            exit(1)
        
        # print(f"DEBUG: {type(node).__name__} type -> {node.type}", file=sys.stderr)

    def visit_ClassRefExpr(self, node, context):
        class_record = self.s.lookup_class(node.class_name)

        if class_record:
            node.type = Type_Record('class-literal', node.class_name)
        else:
            print(f"ERROR [{node.start}:{node.end}]: Class ({node.class_name}) was not defined")
            exit(1)

    def visit_IdRefExpr(self, node, context):
        node.node.accept(self)
        node.type = node.node.type