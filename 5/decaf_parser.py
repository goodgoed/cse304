# Seungwon An (Harry), seunan, 115236174
# Andy (Yi Heng) Su, yihsu, 113378005

import sys
import ply.yacc as yacc
from decaf_lexer import tokens
from decaf_compiler import find_column
from decaf_ast import *

start = 'program'

precedence = (
    ('right', 'ASSIGN'),
    ('nonassoc', 'COMP','LT','GT','LEQ','GEQ','EQUAL', 'AND', 'OR', 'NOTEQUAL'),
    ('left', 'PLUSMINUS', 'PLUS', 'MINUS'),
    ('left', 'TIMESDIVIDE', 'TIMES', 'DIVIDE', "MODULUS"),
    ('right', 'UNARY'),
)

def p_empty(p):
    'empty :'
    p[0] = ''

def p_program(p):
    '''program  : class_decl_list'''
    p[0] = Program(p[1])

def p_class_decl_list(p):
    '''class_decl_list : class_decl_list class_decl
                       | empty'''
    if len(p) == 2:
        p[0] = []
    else:
        p[1].append(p[2].getBody())
        p[0] = p[1]
    

def p_class_decl(p):
    'class_decl : CLASS ID extends_statement LCURLY class_body RCURLY'
    p[0] = ClassDecl(p[2], p[3], p[5].getBody())

def p_extends_statement(p):
    '''extends_statement : EXTENDS ID 
                         | empty'''
    if len(p) == 2:
        p[0] = ''
    else:
        p[0] = p[2]

def p_class_body_decl(p):
    '''class_body_decl  : field_decl
                        | method_decl
                        | constructor_decl'''
    p[0] = p[1].getBody()

def p_class_body(p):
    '''class_body   : class_body class_body_decl
                    | empty'''
    if len(p) == 2:
        p[0] = ClassBody()
    else:
        p[1].decl_list.append(p[2])
        p[0] = p[1]

def p_field_decl(p):
    'field_decl : modifier var_decl'
    
    p[0] = FieldDecl(p[1].getVisibility(), p[1].getApplicability(), p[2].getType(), p[2].getVariables())

def p_method_decl(p):
    'method_decl : modifier type_with_void LPAREN formals RPAREN block'

    p[0] = MethodDecl(p[2].getName(), p[1].getVisibility(), p[1].getApplicability(), p[2].getType(), p[4], p[6].getBody())

def p_constructor_decl(p):
    'constructor_decl : modifier ID LPAREN formals RPAREN block'
    
    p[0] = ConstructorDecl(p[2], p[1].getVisibility(), p[4], p[6].getBody())

def p_var_decl(p):
    '''var_decl : type variables SEMICOLON'''
    p[0] = VarDeclStmt(p[1].getBody(), p[2], p[1].getStart(), p.lineno(3))

def p_variable(p):
    '''variable : ID'''
    p[0] = Variable(p[1], p.lineno(1), p.lineno(1))

def p_variables(p):
    '''variables : variables COMMA variable
                 | variable'''
    if len(p) == 2:
        p[0] = [p[1].getBody()]
    else:
        p[1].append(p[3].getBody())
        p[0] = p[1]

def p_modifier(p):
    '''modifier : access_modifier STATIC
                | access_modifier
                | STATIC
                | empty'''
    if p[1]:
        if p[1] == 'static':
            p[0] = Modifier("private", p[1])
        elif len(p) == 2:
            p[0] = Modifier(p[1], "instance")
        else:
            p[0] = Modifier(p[1], p[2])
    else:
        p[0] = Modifier("private", "instance")

def p_access_modifier(p):
    '''access_modifier  : PUBLIC 
                        | PRIVATE'''
    p[0] = p[1]

def p_type(p):
    '''type : INT 
            | FLOAT 
            | BOOLEAN 
            | ID'''
    p[0] = Type(p[1], p.lineno(1), p.lineno(1))

def p_type_with_void(p):
    '''type_with_void : type ID
                      | VOID ID'''
    if p[1] == "void":
        p[0] = TypeWithVoid(p[1], p[2])
    else:
        p[0] = TypeWithVoid(p[1].getBody(), p[2])

def p_formal_param(p):
    '''formal_param : type variable'''
    p[0] = VarDeclStmt(p[1].getBody(), p[2].getBody(), p[1].getStart(), p[2].getEnd())

def p_formals(p):
    '''formals  : formals COMMA formal_param
                | formal_param
                | empty'''
    
    if len(p) == 2:
        if not p[1]: p[0] = []
        else: p[0] = [p[1].getBody()]
    else:
        p[1].append(p[3].getBody())
        p[0] = p[1] 

def p_block(p):
    '''block : LCURLY stmt_list RCURLY
             | LCURLY RCURLY'''
    if len(p) == 3:
        p[0] = BlockStmt([], p.lineno(1), p.lineno(2))
    else: 
        p[0] = BlockStmt(p[2].getBody(), p.lineno(1), p[2].getEnd())

def p_stmt_list(p):
    '''stmt_list : stmt_list stmt
                 | stmt'''
    if len(p) == 2:
        p[0] = StmtList([p[1].getBody()], p[1].getStart(), p[1].getEnd())
    else:
        p[0] = StmtList(p[1].getBody() + [p[2].getBody()], p[1].getStart(), p[2].getEnd())

def p_stmt(p):
    '''stmt : stmt_expr SEMICOLON
            | var_decl_stmt
            | block
            | for_stmt
            | if_stmt
            | while_stmt
            | continue_stmt
            | break_stmt
            | return_stmt
            | skip_stmt
    '''
    if len(p) == 2:
        p[0] = Stmt(p[1].getBody(), p[1].getStart(), p[1].getEnd())
    else:
        p[0] = Stmt(p[1].getBody(), p[1].getStart(), p.lineno(2))

def p_stmt_expr(p):
    '''stmt_expr    : method_invocation
                    | assign'''
    p[0] = ExprStmt(p[1].getBody(), p[1].getStart(), p[1].getEnd())

def p_var_decl_stmt(p):
    '''var_decl_stmt : var_decl'''

    p[0] = VarDeclStmt(p[1].getType(), p[1].getVariables(), p[1].getStart(), p[1].getEnd())

def p_if_stmt(p):
    '''if_stmt  : IF LPAREN expr RPAREN stmt else_stmt'''
    
    if p[6].getBody() is None:
        p[0] = IfStmt(p[3].getBody(), p[5].getBody(), p[6].getBody(), p.lineno(1), p[5].getEnd())
    else:
        p[0] = IfStmt(p[3].getBody(), p[5].getBody(), p[6].getBody(), p.lineno(1), p[6].getEnd())

def p_else_stmt(p):
    '''else_stmt    : ELSE stmt
                    | empty'''
    
    if len(p) == 2:
        p[0] = ElseStmt(None, -1, -1)
    else:
        p[0] = ElseStmt(p[2].getBody(), p.lineno(1), p[2].getEnd())

def p_while_stmt(p):
    '''while_stmt   : while_check stmt'''
    p[0] = WhileStmt(p[1].getBody(),p[2].getBody(), p[1].getStart(), p[2].getEnd())

def p_while_check(p):
    '''while_check  : WHILE LPAREN expr RPAREN'''
    p[0] = WhileCheck(p[3].getBody(), p.lineno(1), p.lineno(4))

def p_for_stmt(p):
    '''for_stmt : FOR LPAREN for_init SEMICOLON for_check SEMICOLON for_update RPAREN stmt'''
    p[0] = ForStmt(p[3],p[5],p[7],p[9].getBody(),p.lineno(1),p[9].getEnd())

def p_for_init(p):
    '''for_init : stmt_expr
                | empty'''
    if p[1]:
        p[0] = p[1].getBody()
    else:
        p[0] = p[1]

def p_for_check(p):
    '''for_check    : expr
                    | empty'''
    if p[1]:
        p[0] = p[1].getBody()
    else:
        p[0] = p[1]

def p_for_update(p):
    '''for_update   : stmt_expr
                    | empty'''
    if p[1]:
        p[0] = p[1].getBody()
    else:
        p[0] = p[1]

def p_return_stmt(p):
    '''return_stmt  : RETURN expr SEMICOLON
                    | RETURN SEMICOLON'''
    if len(p) == 4:
        p[0] = ReturnStmt(p[2].getBody(), p.lineno(1), p.lineno(3))
    else:
        p[0] = ReturnStmt('', p.lineno(1), p.lineno(2))

def p_break_stmt(p):
    'break_stmt : BREAK SEMICOLON'
    p[0] = BreakStmt(p.lineno(1), p.lineno(2))

def p_continue_stmt(p):
    'continue_stmt : CONTINUE SEMICOLON'
    p[0] = ContinueStmt(p.lineno(1), p.lineno(2))


def p_skip_stmt(p):
    'skip_stmt : SEMICOLON'
    p[0] = SkipStmt(p.lineno(1), p.lineno(1))


def p_expr(p):
    '''expr : primary
            | unary_expr
            | binary_expr
            | comparison
            | assign
    '''
    p[0] = Expr(p[1].getBody(), p[1].getStart(), p[1].getEnd())

def p_unary_expr(p):
    '''unary_expr : unary_op expr %prec UNARY'''
    p[0] = UnaryExpr(p[1].getBody(), p[2].getBody(), p[1].getStart(), p[2].getEnd())

def p_binary_expr(p):
    '''binary_expr : expr plus_minus_op expr %prec PLUSMINUS
                   | expr times_divide_op expr %prec TIMESDIVIDE
                   | expr bool_op expr
    '''
    p[0] = BinaryExpr(p[2], p[1].getBody(), p[3].getBody(), p[1].getStart(), p[3].getEnd())

def p_comparison(p):
    '''comparison : expr comp_op expr %prec COMP'''
    p[0] = BinaryExpr(p[2], p[1].getBody(), p[3].getBody(), p[1].getStart(), p[3].getEnd())

def p_primary(p):
    '''primary  : literal
                | lhs
                | method_invocation
                | LPAREN expr RPAREN
                | NEW ID LPAREN arguments RPAREN
                | THIS
                | SUPER
    '''
    if p[1] == 'new':
        p[0] = NewObjectExpr(p[2], p[4], p.lineno(1), p.lineno(5))
    elif p[1] == 'this':
        p[0] = ThisExpr(None, p.lineno(1), p.lineno(1))
    elif p[1] == 'super':
        p[0] = SuperExpr(None, p.lineno(1), p.lineno(1))
    elif p[1] == '(':
        p[0] = Parenthesis(p[2].getBody(), p.lineno(1), p.lineno(3))
    else:
        p[0] = Primary(p[1].getBody(), p[1].getStart(), p[1].getEnd())

def p_literal(p):
    '''literal  : INTCONST
                | FLOATCONST
                | STRINGCONST
                | NULL
                | TRUE
                | FALSE
    '''
    if isinstance(p[1], int):
        p[0] = ConstantExpr(p[1], "integer", p.lineno(1), p.lineno(1))
    elif isinstance(p[1], float):
        p[0] = ConstantExpr(p[1], "float", p.lineno(1), p.lineno(1))
    elif p[1] == 'null':
        p[0] = ConstantExpr(None, "null", p.lineno(1), p.lineno(1))
    elif p[1] == 'true':
        p[0] = ConstantExpr(True, "true", p.lineno(1), p.lineno(1))
    elif p[1] == 'false':
        p[0] = ConstantExpr(False, "false", p.lineno(1), p.lineno(1))
    elif isinstance(p[1], str):
        p[0] = ConstantExpr(p[1], "string", p.lineno(1), p.lineno(1))

def p_lhs(p):
    '''lhs : field_access'''
    p[0] = Lhs(p[1].getBody(), p[1].getStart(), p[1].getEnd())

def p_field_access(p):
    '''field_access : primary DOT ID
                    | ID'''
    if len(p) == 4:
        p[0] = FieldAccessExpr(p[1].getBody(), p[3], p[1].getStart(), p.lineno(3))
    else:
        p[0] = IdRefExpr(p[1], p.lineno(1), p.lineno(1))

def p_method_invocation(p):
    'method_invocation : field_access LPAREN arguments RPAREN'
    base = p[1]
    if isinstance(p[1], FieldAccessExpr):
        base = p[1].get_base_name()
        method_name = p[1].get_method_name()
    else:
        method_name = p[1].getBody()
    arguments = p[3]
    p[0] = MethodCallExpr(base, method_name, arguments, p[1].getStart(), p.lineno(4))

def p_arguments(p):
    '''arguments : expr 
                 | expr COMMA arguments 
                 | empty'''
    if len(p) == 2 and p[1]:
        p[0] = [p[1].getBody()]
    elif len(p) == 4:
        p[0] = [p[1].getBody()] + p[3]
    else:
        p[0] = []

def p_assign(p):
    '''assign : lhs ASSIGN expr %prec ASSIGN
              | formal_param ASSIGN expr %prec ASSIGN
              | lhs PLUSPLUS
              | PLUSPLUS lhs
              | lhs MINUSMINUS
              | MINUSMINUS lhs'''
    if len(p) == 4:
        p[0] = AssignExpr(p[1].getBody(), p[3].getBody(), p[1].getStart(), p[3].getEnd())
    elif p[2] == '++' and len(p) == 3:
        p[0] = AutoExpr(p[1].getBody(), p[1].getStart(), p.lineno(2), is_increment=True, is_post=True)
    elif p[1] == '++':
        p[0] = AutoExpr(p[2].getBody(), p.lineno(1), p[2].getEnd(), is_increment=True, is_post=False)
    elif p[2] == '--' and len(p) == 3:
        p[0] = AutoExpr(p[1].getBody(), p[1].getStart(), p.lineno(2), is_increment=False, is_post=True)
    elif p[1] == '--':
        p[0] = AutoExpr(p[2].getBody(), p.lineno(1), p[2].getEnd(), is_increment=False, is_post=False)

def p_plus_minus_op(p):
    '''plus_minus_op : PLUS 
                     | MINUS'''
    p[0] = p[1]

def p_times_divide_op(p):
    '''times_divide_op  : TIMES
                        | DIVIDE
                        | MODULUS'''
    p[0] = p[1]

def p_bool_op(p):
    '''bool_op  : AND
                | OR
                '''
    p[0] = p[1]

def p_comp_op(p):
    '''comp_op  : EQUAL
                | NOTEQUAL
                | LT
                | GT
                | LEQ
                | GEQ'''
    p[0] = p[1]

def p_unary_op(p):
    '''unary_op : PLUS 
                | MINUS
                | NOT'''
    p[0] = UnaryOp(p[1], p.lineno(1), p.lineno(1))

# Error rule for syntax errors
def p_error(p):
    if p:
        print("Syntax error: '%s' at line %d position %d" %(p.value, p.lineno, find_column(p.lexer.lexdata, p.lexer, value=p.value)))
    else:
        print("Syntax error at EOF")
    sys.exit()  

# Build the parser
parser = yacc.yacc()