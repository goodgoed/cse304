# Seungwon An (Harry), seunan, 115236174
# Andy (Yi Heng) Su, yihsu, 113378005

import copy

class ASTNode:
    def accept(self, visitor, context=None):
        return visitor.visit(self, context)

class Program(ASTNode):
    def __init__(self, classes):
        self.classes = classes
        self.result = []

    def __str__(self):
        separator = "--------------------------------------------------------------------------"
        res = f"{separator}\n"
        res += f"{separator}\n".join(str(_class) for _class in self.result)
        res+= separator
        return res

    def getBody(self):
        return self

class ClassDecl(ASTNode):
    def __init__(self, name, super, class_body):
        self.name = name
        self.super = super
        self.class_body = class_body

    def getBody(self):
        return self

class ClassBody(ASTNode):
    def __init__(self):
        self.decl_list = []

    def getBody(self):
        return self

class FieldDecl(ASTNode):
    def __init__(self, visibility, applicability, type, variables):
        self.visibility = visibility
        self.applicability = applicability
        self.type = type
        self.variables = variables

    def getBody(self):
        return self

class MethodDecl(ASTNode):
    def __init__(self,name, visibility, applicability, return_type, formals, block):
        self.name = name
        self.visibility = visibility
        self.applicability = applicability
        self.return_type = return_type
        self.formals = formals
        self.body = block

    def getBody(self):
        return self

class ConstructorDecl(ASTNode):
    def __init__(self, name, visibility, formals, block):
        self.name = name
        self.visibility = visibility
        self.formals = formals
        self.body = block

    def getBody(self):
        return self

class Modifier(ASTNode):
    def __init__(self, visibility = "private", applicability = "instance"):
        self.visibility = visibility
        self.applicability = applicability
    
    def getVisibility(self):
        return self.visibility
    
    def getApplicability(self):
        return self.applicability

    def getBody(self):
        return self

class Type(ASTNode):
    def __init__(self, type, start, end):
        self.type = type
        self.start = start
        self.end = end

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self.type
    
class Stmt(ASTNode):
    def __init__(self, stmt, start, end):
        self.stmt = stmt
        self.start = start
        self.end = end

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self.stmt
    
class Expr(ASTNode):
    def __init__(self, body, start, end):
        self.body = body
        self.start = start
        self.end = end

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self.body
    
class Variable(ASTNode):
    def __init__(self, variable, start, end):
        self.variable = variable
        self.start = start
        self.end = end

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self.variable
    
class Parenthesis(ASTNode):
    def __init__(self, body, start, end):
        self.body = body
        self.start = start
        self.end = end

    def getBody(self):
        return self.body
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
class StmtList(ASTNode):
    def __init__(self, body, start, end):
        self.body = body
        self.start = start
        self.end = end

    def getBody(self):
        return self.body
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end

class TypeWithVoid(ASTNode):
    def __init__(self, type, name):
        self.type = type
        self.name = name
    
    def getName(self):
        return self.name
    
    def getType(self):
        return self.type

    def getBody(self):
        return None

class VarDeclStmt(ASTNode):
    def __init__(self,type,variables, start, end):
        self.type = type
        self.variables = variables
        self.start = start
        self.end = end

    def __str__(self):
        variable_list = ', '.join(self.variables)
        return f'{self.type} {variable_list};'
    
    def getType(self):
        return self.type
    
    def getVariables(self):
        return self.variables
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class IfStmt(ASTNode):
    def __init__(self, condition, then_stmt, else_stmt, start, end):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt if else_stmt else SkipStmt(end, end)
        self.start = start
        self.end = end

        self.children = ['condition', 'then_stmt', 'else_stmt']
    
    def __str__(self):
        res = f"If({self.condition}, {self.then_stmt}, {self.else_stmt})"
        return res
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class ElseStmt(ASTNode):
    def __init__(self, body, start, end):
        self.body = body
        self.start = start
        self.end = end

    def getBody(self):
        return self.body
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end

class WhileStmt(ASTNode):
    def __init__(self, condition, body, start, end):
        self.condition = condition
        self.body = body
        self.start = start
        self.end = end

        self.children = ['condition', 'body']
    
    def __str__(self):
        res = f"While({self.condition}, {self.body})"
        return res
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class WhileCheck(ASTNode):
    def __init__(self, body, start, end):
        self.body = body
        self.start = start
        self.end = end

    def getBody(self):
        return self.body

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end

class ForStmt(ASTNode):
    def __init__(self, initializer, condition, update, body, start, end):
        self.initializer = initializer if initializer else SkipStmt(start, end)
        self.condition = condition if condition else SkipStmt(start, end)
        self.update = update if update else SkipStmt(start, end)
        self.body = body
        self.start = start
        self.end = end

        self.children = ['initializer', 'condition', 'update', 'body']

    def __str__(self):
        res = f"For({self.initializer}, {self.condition}, {self.update}, {self.body})"
        return res
    
    def getBody(self):
        return self
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
class ReturnStmt(ASTNode):
    def __init__(self, expr, start, end):
        self.expr = expr
        self.start = start
        self.end = end

        self.children = ['expr']

    def __str__(self):
        res = f"Return({self.expr})"
        return res
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class ExprStmt(ASTNode):
    def __init__(self, expr, start, end):
        self.expr = expr
        self.start = start
        self.end = end

        self.children = ['expr']

    def __str__(self):
        res = f"Expr({self.expr})"
        return res
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class BlockStmt(ASTNode):
    def __init__(self, stmt_list, start, end):
        self.stmt_list = stmt_list
        self.start = start
        self.end = end

    def __str__(self):
        res = "Block([\n"
        if len(self.stmt_list) > 0:
            res += ",\n".join(str(stmt) for stmt in self.stmt_list if not isinstance(stmt, VarDeclStmt))
            res += '\n'
        res += "])"
        return res

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class BreakStmt(ASTNode):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        res = "Break()"
        return res
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class ContinueStmt(ASTNode):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        res = "Continue()"
        return res
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class SkipStmt(ASTNode):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __str__(self):
        res = "Skip()"
        return res

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end

    def getBody(self):
        return self

class ConstantExpr(ASTNode):
    def __init__(self, value, constant_type, start, end):
        self.value = value
        self.constant_type = constant_type
        self.start = start
        self.end = end

    def __str__(self):
        if self.constant_type == "integer":
            return f"Constant(Integer-constant({self.value}))"
        elif self.constant_type == "float":
            return f"Constant(Float-constant({self.value}))"
        elif self.constant_type == "string":
            return f"Constant(String-constant({self.value}))"
        elif self.constant_type == "null":
            return "Constant(Null)"
        elif self.constant_type == "true":
            return "Constant(True)"
        elif self.constant_type == "false":
            return "Constant(False)"
        else:
            return f"Constant(Unknown-constant({self.value}))"

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class Lhs(ASTNode):
    def __init__(self, body, start, end):
        self.body = body
        self.start = start
        self.end = end

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self.body

class VarExpr(ASTNode):
    def __init__(self, variable_name):
        self.variable_name = variable_name
        self.id = -1

    def __str__(self):
        return f"Variable({self.id})"    
    
    def getBody(self):
        return self.body

class UnaryExpr(ASTNode):
    def __init__(self, operator, operand, start, end):
        operator_table = {
            '+': 'plus',
            '-': 'uminus',
            '!': 'neg'
        }
        self.operator = operator_table[operator]
        self.operand = operand
        self.start = start
        self.end = end

        self.children = ['operand']
    
    def __str__(self):
        return f"Unary({self.operator}, {self.operand})" if self.operator != 'plus' else f'{self.operand}'

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class UnaryOp(ASTNode):
    def __init__(self, body, start, end):
        self.body = body
        self.start = start
        self.end = end

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self.body

class BinaryExpr(ASTNode):
    def __init__(self, operator, left_operand, right_operand, start, end):
        operator_table = {
            '+': 'add',
            '-': 'sub',
            '*': 'mul',
            '/': 'div',
            '&&': 'and',
            '||': 'or',
            '==': 'eq',
            '!=': 'neq',
            '<': 'lt',
            '<=': 'leq',
            '>': 'gt',
            '>=': 'geq'
        }

        self.operator = operator_table[operator]
        self.left_operand = left_operand
        self.right_operand = right_operand
        self.start = start
        self.end = end

        self.children = ['left_operand','right_operand']

    def __str__(self):
        return f"Binary({self.operator}, {self.left_operand}, {self.right_operand})"

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end

    def getBody(self):
        return self

class AssignExpr(ASTNode):
    def __init__(self, left_operand, right_operand, start, end):
        self.left_operand = left_operand
        self.right_operand = right_operand
        self.left_type = None
        self.right_type = None
        self.start = start
        self.end = end

        self.children = ['left_operand', 'right_operand']

    def __str__(self):
        return f"Assign({self.left_operand}, {self.right_operand}, {self.left_type}, {self.right_type})"
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class AutoExpr(ASTNode):
    def __init__(self, operand, start, end, is_increment, is_post):
        self.operand = operand
        self.is_increment = is_increment
        self.is_post = is_post
        self.start = start
        self.end = end
    
        self.children = ['operand']

    def __str__(self):
        increment_str = "inc" if self.is_increment else "dec"
        post_str = "post" if self.is_post else "pre"
        return f"Auto({self.operand}, {increment_str}, {post_str})"

    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class FieldAccessExpr(ASTNode):
    def __init__(self, base, field_name, start, end):
        self.base = base
        self.field_name = field_name
        self.id = -1
        self.start = start
        self.end = end

        self.children = ['base']

    def __str__(self):
        return f"Field-access({self.base}, {self.field_name}, {self.id})"

    def get_method_name(self):
        return self.field_name

    def get_base_name(self):
        return self.base
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self
        
class MethodCallExpr(ASTNode):
    def __init__(self, base, method_name, arguments, start, end):
        self.base = base
        self.method_name = method_name
        self.arguments = arguments
        self.start = start
        self.end = end

        self.children = ['base', 'arguments']

    def __str__(self):
        arg_list = ", ".join(str(arg) for arg in self.arguments)
        return f"Method-call({self.base}, {self.method_name}, [{arg_list}])"
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class NewObjectExpr(ASTNode):
    def __init__(self, class_name, constructor_args, start, end):
        self.class_name = class_name
        self.constructor_args = constructor_args
        self.start = start
        self.end = end

        self.children = ['constructor_args']

    def __str__(self):
        arg_list = ", ".join(str(arg) for arg in self.constructor_args)
        return f"New-object({self.class_name}, [{arg_list}])"
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class Primary(ASTNode):
    def __init__(self, body, start, end):
        self.body = body
        self.start = start
        self.end = end

    def getBody(self):
        return self.body
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end

class ThisExpr(ASTNode):
    def __init__(self, body, start, end):
        self.start = start
        self.end = end
        self.body = body

    def __str__(self):
        return "This"
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class SuperExpr(ASTNode):
    def __init__(self, body, start, end):
        self.start = start
        self.end = end
        self.body = body

    def __str__(self):
        return "Super"
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self

class ClassRefExpr(ASTNode):
    def __init__(self, name):
        self.class_name = name

    def __str__(self):
        return f"Class({self.class_name})"
    
    def getBody(self):
        return self.body

class IdRefExpr(ASTNode):
    def __init__(self, id, start, end):
        self.id = id
        self.node = None
        self.start = start
        self.end = end

    def __str__(self):
        return str(self.node)
    
    def getStart(self):
        return self.start
    
    def getEnd(self):
        return self.end
    
    def getBody(self):
        return self
    
##RECORDS##

class Class_Record(ASTNode):
    def __init__(self, name, super, constructors, methods, fields):
        self.name = name
        self.super = super
        self.constructors = constructors
        self.methods = methods
        self.fields = fields
    
    def __str__(self):
        res=f"Class Name: {self.name}\n"
        res+=f"Superclass Name: {self.super}\n"
        res+=f"Fields:\n"
        for field in self.fields:
            res+=f"{field}\n"
        res+=f"Constructors:\n"
        for constructor in self.constructors:
            res+=f"{constructor}\n"
        res+=f"Methods:\n"
        for method in self.methods:
            res+=f"{method}\n"
        return res
    
    def __getitem__(self, key):
        data_map = {
            'name': self.name,
            'super_class': self.super,
            'constructors': self.constructors,
            'methods': self.methods,
            'fields': self.fields,
        }
        return data_map.get(key, None) 

class Constructor_Record(ASTNode):
    def __init__(self, id, visibility, parameters, variable_table, body):
        self.id = id
        self.visibility = visibility
        self.parameters = parameters
        self.variable_table = variable_table
        self.body = body
    
    def __str__(self):
        res = f"CONSTRUCTOR: {self.id}, {self.visibility}\n"
        res += "Constructor Parameters: "
        res += ", ".join(str(formal.id) for formal in self.parameters)
        res += f"\nVariable Table:\n"
        for variable in self.variable_table.values():
            res += f"{variable}\n"
        res += "Constructor Body:\n"
        res += f"{self.body}"

        return res

class Method_Record(ASTNode):
    def __init__(self, name, id, containing_class, visibility, applicability, parameters, return_type, variable_table, body):
        self.name = name
        self.id = id
        self.containing_class = containing_class
        self.visibility = visibility
        self.applicability = applicability
        self.parameters = parameters
        self.return_type = return_type
        self.variable_table = variable_table
        self.body = body

    def __str__(self):
        res = f"METHOD: {self.id}, {self.name}, {self.containing_class}, {self.visibility}, {self.applicability}, {self.return_type.prettyPrint()}\n"
        res += "Method Parameters: "
        res += ", ".join(str(formal.id) for formal in self.parameters)
        res += "\nVariable Table:\n"
        for variable in self.variable_table.values():
            res += f"{variable}\n"
        res += "Method Body:\n"
        res += f"{self.body}"

        return res

class Field_Record(ASTNode):
    def __init__(self, name, id, containing_class, visibility, applicability, type):
        self.name = name
        self.id = id
        self.containing_class = containing_class
        self.visibility = visibility
        self.applicability = applicability
        self.type = type    
    
    def __str__(self):
        res = f"FIELD: {self.id}, {self.name}, {self.containing_class}, {self.visibility}, {self.applicability}, {self.type.prettyPrint()}"
        return res 
    
    def __getitem__(self, key):
        data_map = {
            'name': self.name,
            'id': self.id,
            'containing_class': self.containing_class,
            'visibility': self.visibility,
            'applicability': self.applicability,
            'type': self.type
        }
        return data_map.get(key, None) 

class Variable_Record(ASTNode):
    def __init__(self, name, id, kind, type):
        self.name = name
        self.id = id
        self.kind = kind
        self.type = type

    def __str__(self):
        res = f'VARIABLE: {self.id}, {self.name}, {self.kind}, {self.type.prettyPrint()}'
        return res
    
    def get_id(self):
        return self.id

class Type_Record(ASTNode):
    # type = primitive types | user types | class-literal
    # type_obj is only given when type is class-literal

    def __init__(self, type, type_obj = None):
        if type in ('int', 'float', 'string', 'boolean', 'void', 'error', 'null'):
            self.type = type
            self.type_obj = type_obj
        elif type == 'class-literal':
            self.type = type
            self.type_obj = type_obj
        else:
            self.type = 'user'
            self.type_obj = type

    def __str__(self):
        if self.type in ('int', 'float', 'string', 'boolean', 'void', 'error', 'null'):
            return self.type
        elif self.type == 'class-literal':
            return f"class-literal({self.type_obj})"
        elif self.type == 'user':
            return f"{self.type_obj}"

    def getType(self):
        return self.type
    
    def isNumeric(self):
        return self.type in ('int', 'float')
    
    def isInt(self):
        return self.type == 'int'
    
    def isFloat(self):
        return self.type == 'float'

    def isString(self):
        return self.type == 'string'
    
    def isBoolean(self):
        return self.type == 'boolean'
    
    def isVoid(self):
        return self.type == 'void'

    def isError(self):
        return self.type == 'error'
    
    def isNull(self):
        return self.type == 'null'

    def isClassLiteral(self):
        return self.type == 'class-literal'

    def isUserDefined(self):
        return self.type == 'user'
    
    # Type can be either string or Type_Record instance
    def equals(self, type):
        if isinstance(type, str):
            return self.type == type
        elif isinstance(type, Type_Record):
            if self.type == type.type:
                if type.type in ('user', 'class-literal'):
                    return self.type_obj == type.type_obj
                else:
                    return True
            else:
                return False
        else:
            return False
    
    def copy(self):
        if self.type == 'user':
            return Type_Record(self.type_obj)
        elif self.type == 'class-literal':
            return Type_Record('class-literal', self.type_obj)
        else:
            return Type_Record(self.type)

    def prettyPrint(self):
        if self.type == 'user':
            return f"user({self.type_obj})"
        elif self.type == 'class-literal':
            return f"class-literal({self.type_obj})"
        else:
            return self.type

##SYMBOL TABLE##

class Symbol_Table():
    def __init__(self):
        self.variable_stack = []
        self.variable_table = []
        self.variable_id_counter = 1

        self.formals = []
        
        self.class_table = {
            'In': Class_Record(
                name='In',
                super='',
                constructors=[],
                methods=[
                    Method_Record(
                        name="scan_int",
                        id=None,
                        containing_class='In',
                        visibility='public',
                        applicability='static',
                        parameters=[],
                        return_type=Type_Record('int'),
                        variable_table = {},
                        body=[]
                    ),
                    Method_Record(
                        name="scan_float",
                        id=None,
                        containing_class='In',
                        visibility='public',
                        applicability='static',
                        parameters=[],
                        return_type=Type_Record('float'),
                        variable_table = {},
                        body=[]
                    ),
                ],
                fields=[]
            ),
            'Out': Class_Record(
                name='Out',
                super='',
                constructors=[],
                methods=[
                    # Method_Record(
                    #     name="print",
                    #     id=None,
                    #     containing_class=None,
                    #     visibility='public',
                    #     applicability='static',
                    #     parameters=[
                    #         Variable_Record(
                    #             id=None,
                    #             name='i',
                    #             kind='formal',
                    #             type='int'
                    #         )
                    #     ],
                    #     return_type=None,
                    #     variable_table = {},
                    #     body=[]
                    # ),
                    # Method_Record(
                    #     name="print",
                    #     id=None,
                    #     containing_class=None,
                    #     visibility='public',
                    #     applicability='static',
                    #     parameters=[
                    #         Variable_Record(
                    #             id=None,
                    #             name='f',
                    #             kind='formal',
                    #             type='float'
                    #         )
                    #     ],
                    #     return_type=None,
                    #     variable_table = {},
                    #     body=[]
                    # ),
                    # Method_Record(
                    #     name="print",
                    #     id=None,
                    #     containing_class=None,
                    #     visibility='public',
                    #     applicability='static',
                    #     parameters=[
                    #         Variable_Record(
                    #             id=None,
                    #             name='b',
                    #             kind='formal',
                    #             type='boolean'
                    #         )
                    #     ],
                    #     return_type=None,
                    #     variable_table = {},
                    #     body=[]
                    # ),
                    Method_Record(
                        name="print",
                        id=None,
                        containing_class=None,
                        visibility='public',
                        applicability='static',
                        parameters=[
                            Variable_Record(
                                id=None,
                                name='s',
                                kind='formal',
                                type='string'
                            )
                        ],
                        return_type=Type_Record('void'),
                        variable_table = {},
                        body=[]
                    ),
                ],
                fields=[]
            )
        }
        self.current_class = None
        self.constructor_id_counter = 1
        self.method_id_counter = 1
        self.field_id_counter = 1
    
    def set_formals(self, formals):
        self.formals = formals

    def add_constructor(self, visibility, body):
        parameters = []
        for variable in self.variable_table[-1].values():
            if variable.kind == 'formal': parameters.append(variable)
        constructor_record = Constructor_Record(self.constructor_id_counter, visibility, parameters, self.variable_table[-1], body)
        self.current_class['constructors'].append(constructor_record)
        self.constructor_id_counter+=1
    
    def add_method(self, name, visibility, applicability,return_type, body):
        containing_class = self.current_class['name']
        parameters = []
        for variable in self.variable_table[-1].values():
            if variable.kind == 'formal': parameters.append(variable)

        type_record = Type_Record(return_type)
        method_record = Method_Record(name, self.method_id_counter, containing_class, visibility, applicability, parameters, type_record, self.variable_table[-1], body)
        self.current_class['methods'].append(method_record)
        self.method_id_counter+=1
    
    def add_field(self, name, visibility, applicability, type):
        lookup_field = self.lookup_field(name)
        if lookup_field and lookup_field['containing_class'] == self.current_class['name']:
            print("ERROR: two fields should have distinct name in a class")
            exit(1)

        containing_class = self.current_class['name']
        type_record = Type_Record(type)
        field_record = Field_Record(name, self.field_id_counter, containing_class, visibility, applicability, type_record)
        self.current_class['fields'].append(field_record)
        self.field_id_counter+=1
    
    def add_variable(self, name, kind, type):
        if name in self.variable_stack[-1]:
            print(f"ERROR: two varialbes inside the block should have distinct name")
            exit(1)

        t_record = Type_Record(type)
        v_record = Variable_Record(name, self.variable_id_counter, kind, t_record)

        self.variable_stack[-1][name] = v_record
        self.variable_id_counter+=1

    def enter_class(self,name,super_class):
        if self.lookup_class(name):
            print("ERROR: two classes should have distinct name")
            exit(1)

        self.current_class = {
            'name': name,
            'super_class': super_class,
            'constructors': [],
            'methods': [],
            'fields': []
        }
    
    def exit_class(self):
        if self.current_class == None:
            print("Cannot exit global scope!")
            exit(1)

        name = self.current_class['name']
        super_class = self.current_class['super_class']
        constructors = copy.deepcopy(self.current_class['constructors'])
        methods = copy.deepcopy(self.current_class['methods'])
        fields = copy.deepcopy(self.current_class['fields'])

        c_record = Class_Record(name, super_class, constructors, methods, fields)
        self.class_table[name] = c_record
        self.current_class = None
        self.variable_id_counter = 1
        return c_record
    
    def enter_block(self):
        self.variable_stack.append({})
        for formal in self.formals:
            if not formal.getVariables(): 
                continue
            name = formal.getVariables()
            type = formal.getType()
            kind = 'formal'
            type_record = Type_Record(type)
            variable_record = Variable_Record(name, self.variable_id_counter, kind, type_record)
            
            self.variable_stack[-1][name] = variable_record
            self.variable_id_counter+=1
        self.formals = []
    
    def exit_block(self):
        self.variable_table.append(self.variable_stack.pop())
        self.formals = []
    
    def lookup_variable(self, name):
        for scope in reversed(self.variable_stack):
            if name in scope:
                return scope[name]

        return None
    
    def lookup_method(self, id):
        for _class in self.class_table.values():
            for method in _class.methods:
                if id == method.id:
                    return method
        return None
    
    def lookup_method_by_name(self, current_class, name):
        current_class = self.lookup_class(current_class)
        if not current_class:
            return None
        
        while current_class:
            for method in current_class.methods:
                if method.name == name:
                    return method
            current_class = self.lookup_class(current_class['super_class'])
        
        return None

    def get_current_class(self):
        return self.current_class

    def lookup_class(self,name):
        return self.class_table.get(name)

    def lookup_field(self, field_name, current_class = None):
        #Iteratively looks up the fields in super class
        current_class = current_class if current_class else self.current_class

        while current_class:
            for field in current_class['fields']:
                if field['name'] == field_name: 
                    return field

            current_class = self.lookup_class(current_class['super_class'])
        return None