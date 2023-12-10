from decaf_visitor import NodeVisitor
from decaf_ast import FieldAccessExpr
import pdb

class CodeGenerator(NodeVisitor):
    def __init__(self, s, mi):
        self.code = ""
        self.s = s
        self.mi = mi #machine instruction
        self.current_class_record = None
        self.loop_context = {
            'break': "",
            'continue': ""
        }
        self.auto_context = {
            'is_post': False,
            'instruction': ""
        }

    def emit(self, code):
        self.code = self.code + code

    def visit_Program(self, node, context):
        for _class in node.result:
            _class.accept(self)
        
        self.code = self.mi.static_directive() + "\n" + self.code

    def visit_Class_Record(self, node, context):
        #try to look for the most super class and set offset for every field
        self.current_class_record = node
        self.emit(f"#===={node.name}====\n")
        
        #Find the super class
        super_class = self.s.lookup_class(node['super_class'])
        super_class = super_class if super_class else node
        
        class_name = super_class.name
        if super_class is not node:
            self.mi.restore_info(class_name)
        for field in node.fields:
            self.mi.set_offset(field.id, field.applicability)

        for constructor in node.constructors:
            constructor.accept(self)
        for method in node.methods:
            method.accept(self)

        self.mi.reset(node.name)

    def visit_Constructor_Record(self, node, context):
        label = f"C_{node.id}:\n"
        self.emit(label)
        for variable in node.variable_table.values():
            self.mi.bind_variable(variable.id, variable.kind)
        
        node.body.accept(self)

        self.mi.reset_arguments()

    def visit_Method_Record(self, node, context):
        label = f"M_{node.name}_{node.id}:\n"
        self.emit(label)
        for variable in node.variable_table.values():
            self.mi.bind_variable(variable.id, variable.kind)

        node.body.accept(self)
        
        self.mi.reset_arguments()

    def visit_IfStmt(self, node, context):
        condition_result_register = node.condition.accept(self)
        
        code = ""

        true_label = self.mi.assign_label("IF_", "_TRUE")
        done_label = self.mi.assign_label("IF_", "_DONE")

        code += self.mi.branch(condition_result_register, true_label, True)
        self.emit(code) #fflush the code to the state variable
        #Print out statements inside else stmt
        node.else_stmt.accept(self)
        code = self.mi.branch(None, done_label, None)
        code += self.mi.label(true_label)
        self.emit(code)
        #Print out statements inside then stmt
        node.then_stmt.accept(self)
        code = self.mi.label(done_label)

        self.emit(code)

    def visit_WhileStmt(self, node, context):
        code = ""

        check_label = self.mi.assign_label("WHILE_","_CHECK")
        done_label = self.mi.assign_label("WHILE_","_DONE")

        #Set loop context
        self.loop_context['break'] = done_label
        self.loop_context['continue'] = check_label

        self.emit(self.mi.label(check_label))
        condition_result_register = node.condition.accept(self)
        code += self.mi.branch(condition_result_register, done_label, False)
        self.emit(code)
        node.body.accept(self) #Print the stmt inside the loop body
        code = self.mi.branch(None, check_label, None)

        code += self.mi.label(done_label)
        self.emit(code)

        #Unset loop context
        self.loop_context['break'] = ""
        self.loop_context['continue'] = ""
        
    def visit_ForStmt(self, node, context):
        node.initializer.accept(self)

        code = ""

        check_label = self.mi.assign_label("FOR_","_CHECK")
        update_label = self.mi.assign_label("FOR_","_UPDATE")
        done_label = self.mi.assign_label("FOR_","_DONE")

        #Set loop context
        self.loop_context['break'] = done_label
        self.loop_context['continue'] = update_label

        #Initializer
        self.emit(self.mi.label(check_label))
        condition_result_register = node.condition.accept(self)

        #loop body starts
        self.emit(self.mi.branch(condition_result_register, done_label, False))
        node.body.accept(self)

        #update
        self.emit(self.mi.label(update_label))
        node.update.accept(self)
        code = self.mi.branch(None, check_label, None)
        code += self.mi.label(done_label)

        self.emit(code)

        #Unset loop context
        self.loop_context['break'] = ""
        self.loop_context['continue'] = ""

    def visit_ReturnStmt(self, node, context):
        result_register = node.expr.accept(self)

        code = ""
        code += self.mi.move('a0', result_register)
        code += self.mi.ret()

        self.emit(code)

    def visit_ExprStmt(self, node, context):
        node.expr.accept(self,context)

        #handle post increment
        if self.auto_context['is_post']:
            self.emit(self.auto_context['instruction'])
            #unset auto context
            self.auto_context['is_post'] = False
            self.auto_context['instruction'] = ""

    def visit_BlockStmt(self, node, context):
        for stmt in node.stmt_list:
            stmt.accept(self)

    def visit_BreakStmt(self, node, context):
        label = self.loop_context['break']
        self.emit(self.mi.branch(None, label, None))

    def visit_ContinueStmt(self, node, context):
        label = self.loop_context['continue']
        self.emit(self.mi.branch(None, label, None))

    def visit_ConstantExpr(self, node, context):
        result = self.mi.assign_register()
        value = node.value
        type = node.type.type

        if type == 'boolean':
            value = 1 if value else 0

        code = self.mi.move_constant(result, value, type)
        
        self.emit(code)
        return result

    def visit_VarExpr(self, node, context):
        return self.mi.bind_variable(node.id)

    def visit_UnaryExpr(self, node, context):
        operand_result_register = node.operand.accept(self)
        operator = node.operator
        operand_type = node.operand.type.type

        result = self.mi.assign_register()
        if operator == 'uminus':
            minus_one = self.mi.assign_register()
            self.emit(self.mi.move_constant(minus_one, -1, operand_type))
            self.emit(self.mi.mul(result, minus_one, operand_result_register, operand_type))
        elif operator == 'neg':
            one = self.mi.assign_register()
            self.emit(self.mi.move_constant(one, 1, operand_type))
            self.emit(self.mi.sub(result, one, operand_result_register, operand_type))
        elif operator == 'plus':
            self.emit(self.mi.move(result, operand_result_register))

        return result

    def visit_BinaryExpr(self, node, context):
        left_result_register = node.left_operand.accept(self)
        right_result_register = node.right_operand.accept(self)

        operator = node.operator
        left_type = node.left_operand.type.type
        right_type = node.right_operand.type.type
        required_type = left_type #Set any type of two for now

        code = ""

        #Convert type to match if the operator is not boolean operator
        if operator not in ('and', 'or') and left_type != right_type:
            if left_type == 'int':
                temp = self.mi.assign_register()
                code += self.mi.convert(temp, left_result_register, 'float')
                left_result_register = temp
                required_type = 'float'
            elif right_type == 'int':
                temp = self.mi.assign_register()
                code += self.mi.convert(temp, right_result_register, 'float')
                right_result_register = temp
                required_type = 'float'

        result = self.mi.assign_register()
        if operator == 'add':
            code += self.mi.add(result, left_result_register, right_result_register, required_type)
        elif operator == 'sub':
            code += self.mi.sub(result, left_result_register, right_result_register, required_type)
        elif operator == 'mul':
            code += self.mi.mul(result, left_result_register, right_result_register, required_type)
        elif operator == 'div':
            code += self.mi.div(result, left_result_register, right_result_register, required_type)
        elif operator == 'and':
            code += self.mi.mul(result, left_result_register, right_result_register, required_type)
        elif operator == 'or':
            temp = self.mi.assign_register()
            true_label = self.mi.assign_label("OR_","_TRUE")
            done_label = self.mi.assign_label("OR_","_DONE")

            code += self.mi.add(temp, left_result_register, right_result_register, type)
            code += self.mi.branch(temp, true_label, True)
            code += self.mi.move_constant(result, 0, 'int')
            code += self.mi.branch(None, done_label, None)
            code += self.mi.label(true_label)
            code += self.mi.move_constant(result, 1, 'int')
            code += self.mi.label(done_label)
        elif operator == 'eq':
            temp = self.mi.assign_register()
            false_label = self.mi.assign_label("EQ_","_FALSE")
            done_label = self.mi.assign_label("EQ_","_DONE")

            code += self.mi.sub(temp, left_result_register,right_result_register, type)
            code += self.mi.branch(temp, false_label, True)#Jump to label_1 if not equal
            code += self.mi.move_constant(result, 1, 'int')
            code += self.mi.branch(None, done_label, None)
            code += self.mi.label(false_label)
            code += self.mi.move_constant(result, 0, 'int')
            code += self.mi.label(done_label)
        elif operator == 'neq':
            temp = self.mi.assign_register()
            true_label = self.mi.assign_label("NEQ_","_TRUE")
            done_label = self.mi.assign_label("NEQ_","_DONE")

            code += self.mi.sub(temp, left_result_register,right_result_register, type)
            code += self.mi.branch(temp, true_label, True)#Jump to label_1 if not equal
            code += self.mi.move_constant(result, 0, 'int')
            code += self.mi.branch(None, done_label, None)
            code += self.mi.label(true_label)
            code += self.mi.move_constant(result, 1, 'int')
            code += self.mi.label(done_label)
        elif operator == 'lt':
            code += self.mi.lt(result, left_result_register, right_result_register, required_type)
        elif operator == 'leq':
            code += self.mi.leq(result, left_result_register, right_result_register, required_type)
        elif operator == 'gt':
            code += self.mi.gt(result, left_result_register,  right_result_register,required_type)
        elif operator == 'geq':
            code += self.mi.geq(result, left_result_register, right_result_register, required_type)

        self.emit(code)
        return result

    def visit_AssignExpr(self, node, context): 
        left_type = node.left_operand.type
        right_type = node.right_operand.type
        context = None
        #do hload when type of lhs is 'user' or 'class-literal'
        if isinstance(node.left_operand, FieldAccessExpr):
            context = {
                'store_required': True
            }

        left_result_register = node.left_operand.accept(self,context)
        right_result_register = node.right_operand.accept(self)

        #convert before assign if the type is numeric and they are not equal
        if not left_type.equals(right_type) and left_type.isNumeric():
            converted = self.mi.assign_register()

            self.emit(self.mi.convert(converted, right_result_register, left_type.type))
            right_result_register = converted
            
        if isinstance(node.left_operand, FieldAccessExpr):
            base_address_register, offset = left_result_register
            self.emit(self.mi.hstore(base_address_register, offset, right_result_register))
        else:
            self.emit(self.mi.move(left_result_register, right_result_register))

        #handle post increment
        if self.auto_context['is_post']:
            self.emit(self.auto_context['instruction'])
            #unset auto context
            self.auto_context['is_post'] = False
            self.auto_context['instruction'] = ""

    def visit_AutoExpr(self, node, context):
        operand_result_register = node.operand.accept(self)
        operand_type = node.operand.type.type

        code = ""

        one = self.mi.assign_register()
        code += self.mi.move_constant(one, 1, operand_type)
        if node.is_post:
            if node.is_increment:
                code += self.mi.add(operand_result_register, operand_result_register, one, operand_type)
            else:
                code += self.mi.sub(operand_result_register, operand_result_register, one, operand_type)
            self.auto_context['is_post'] = True
            self.auto_context['instruction'] = code
        else:
            if node.is_increment:
                code += self.mi.add(operand_result_register, operand_result_register, one, operand_type)
            else:
                code += self.mi.sub(operand_result_register, operand_result_register, one, operand_type)
            self.emit(code)

        return operand_result_register

    def visit_FieldAccessExpr(self, node, context):
        base_register = node.base.accept(self)
        
        field_id = node.id
        field_offset = self.mi.get_offset(field_id)
        field_offset_register = self.mi.assign_register()

        self.emit(self.mi.move_constant(field_offset_register, field_offset, 'int'))
        if context and context['store_required']:
            return (base_register, field_offset_register)
        else:
            result = self.mi.assign_register()
            self.emit(self.mi.hload(result, base_register, field_offset_register))
            return result
        
    def visit_MethodCallExpr(self, node, context):
        base_address_register = node.base.accept(self)

        code = ""
        name = node.method_name
        id = node.id
        arguments = node.arguments
        argument_registers = []

        result_register = self.mi.assign_register()
        for argument in arguments:
            argument_register = argument.accept(self)
            argument_registers.append(argument_register)
        code += self.mi.save_arguments(len(argument_registers))
        code += self.mi.move('a0', base_address_register)
        for index, argument_register in enumerate(argument_registers):
            code += self.mi.move(f'a{index+1}', argument_register)
        code += self.mi.call(f"M_{name}_{id}") 
        code += self.mi.move(result_register, 'a0')
        code += self.mi.restore_arguments(len(argument_registers))
        
        self.emit(code)

        return result_register

    def visit_NewObjectExpr(self, node, context):
        code = ""
        name = node.class_name
        id = node.id
        arguments = node.constructor_args
        argument_registers = []

        size_register = self.mi.assign_register()
        base_address_register = self.mi.assign_register()

        size = self.mi.get_class_size(name)
        code = self.mi.move_constant(size_register, size, 'int')
        code += self.mi.halloc(base_address_register, size_register)
        self.emit(code)
        for argument in arguments:
            argument_register = argument.accept(self)
            argument_registers.append(argument_register)

        code = self.mi.save_arguments(len(argument_registers))
        code += self.mi.move('a0', base_address_register)
        for index, argument_register in enumerate(argument_registers):
            code += self.mi.move(f'a{index+1}', argument_register)
        code += self.mi.call(f"C_{id}")
        code += self.mi.restore_arguments(len(argument_registers))
        
        self.emit(code)
        return base_address_register

    def visit_ThisExpr(self, node, context):
        return 'a0'

    def visit_SuperExpr(self, node, context):
        return 'a0'

    def visit_ClassRefExpr(self, node, context):
        return 'sap'

    def visit_IdRefExpr(self, node, context):
        return node.node.accept(self)