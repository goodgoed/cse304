from decaf_visitor import NodeVisitor
import pdb

class CodeGenerator(NodeVisitor):
    def __init__(self, mi):
        self.code = ""
        self.mi = mi #machine instruction

    def emit(self, code):
        self.code = self.code + code + "\n"

    def visit_Program(self, node):
        for _class in node.result:
            _class.accept(self)

    def visit_Class_Record(self, node):
        self.variables = dict()

        for field in node.fields:
            field.accept(self)
        for constructor in node.constructors:
            constructor.accept(self)
        for method in node.methods:
            method.accept(self)
        
    def visit_Field_Record(self, node):
        id = node.id
        applicability = node.applicability
        
        self.mi.store_offset(id, applicability)

    def visit_Constructor_Record(self, node):
        label = f"C_{node.id}: "
        self.emit(label)
        node.body.accept(self)

    def visit_Method_Record(self, node):
        label = f"M_{node.name}_{node.id}: "
        self.emit(label)
        #what about arguments
        for variable in node.variable_table.values():
            if variable.kind == 'local':
                self.variables[variable.id] = self.assign_register()

        node.body.accept(self)

    def visit_IfStmt(self, node):
        pass

    def visit_WhileStmt(self, node):
        pass

    def visit_ForStmt(self, node):
        pass

    def visit_ReturnStmt(self, node):
        pass

    def visit_ExprStmt(self, node):
        node.expr.accept(self)

    def visit_BlockStmt(self, node):
        for stmt in node.stmt_list:
            stmt.accept(self)

    def visit_BreakStmt(self, node):
        pass

    def visit_ContinueStmt(self, node):
        pass

    def visit_SkipStmt(self, node):
        pass

    def visit_ConstantExpr(self, node):
        result = self.assign_register()
        self.emit(self.mi.move_constant(result, node.value, node.type.type))
        return result

    def visit_VarExpr(self, node):
        return self.variables[node.id]

    def visit_UnaryExpr(self, node):
        operator = node.operator
        operand_type = node.operand.type
        operand_result_register = node.operand.accept(self)
        result = self.assign_register()

        if operator == 'neg':
            zero_register = self.assign_register()
            self.emit(self.mi.load_immediate(zero_register, 0, operand_type.type))
            self.emit(self.mi.sub(result, zero_register, operand_result_register, operand_type.type))
            

    #TODO boolean values?
    def visit_BinaryExpr(self, node):
        operator = node.operator
        left_type = node.left_operand.type
        right_type = node.right_operand.type
        left_result_register = node.left_operand.accept(self)
        right_result_register = node.right_operand.accept(self)

        #TODO conversion required
        if operator == 'add':
            result = self.assign_register()
            self.emit(self.mi.add(result, left_result_register, right_result_register, left_type.type))
        elif operator == 'sub':
            pass
        elif operator == 'mul':
            result = self.assign_register()
            self.emit(self.mi.mul(result, left_result_register, right_result_register, left_type.type))
        elif operator == 'div':
            pass

        return result

    def visit_AssignExpr(self, node):
        left_result_register = node.left_operand.accept(self)
        right_result_register = node.right_operand.accept(self)

        self.emit(self.mi.move(left_result_register, right_result_register))

    def visit_AutoExpr(self, node):
        pass

    def visit_FieldAccessExpr(self, node):
        instance_register = node.instance.accept(self)
        offset = self.offset[node.field]
        result = self.assign_register()
        self.emit(self.mi.load_field(result, instance_register, offset))
        return result
        
    def visit_MethodCallExpr(self, node):
        pass

    def visit_NewObjectExpr(self, node):
        pass

    def visit_ThisExpr(self, node):
        pass

    def visit_SuperExpr(self, node):
        pass

    def visit_ClassRefExpr(self, node):
        pass

    def visit_IdRefExpr(self, node):
        return node.node.accept(self)