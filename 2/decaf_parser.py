# Seungwon An (Harry), seunan, 115236174
# Andy (Yi Heng) Su, yihsu, 113378005

import sys
import ply.yacc as yacc
from decaf_lexer import tokens
from decaf_checker import find_column

start = 'program'

precedence = (
    ('nonassoc', 'COMP','LT','GT','LEQ','GEQ','EQUAL','NOTEQUAL'),
    ('right', 'ASSIGN'),
    ('left','BOOL'),
    ('left', 'PLUSMINUS', 'PLUS', 'MINUS'),
    ('left', 'TIMESDIVIDE', 'TIMES', 'DIVIDE'),
    ('right', 'UNARY'),
)

def p_empty(p):
    'empty :'

def p_program(p):
    '''program  : class_decl_list'''

def p_class_decl_list(p):
    '''class_decl_list : class_decl class_decl_list
                       | empty'''

def p_class_decl(p):
    'class_decl : CLASS ID extends_statement LCURLY class_body RCURLY'

def p_extends_statement(p):
    '''extends_statement : EXTENDS ID 
                         | empty'''

def p_class_body_decl(p):
    '''class_body_decl  : field_decl
                        | method_decl
                        | constructor_decl'''
    
def p_class_body(p):
    '''class_body : class_body_decl class_body
                    | empty'''

def p_field_decl(p):
    'field_decl : modifier var_decl'

def p_method_decl(p):
    'method_decl : modifier type_with_void LPAREN formals RPAREN block'

def p_constructor_decl(p):
    'constructor_decl : modifier ID LPAREN formals RPAREN block'

def p_var_decl(p):
    '''var_decl : type variables SEMICOLON'''

def p_variable(p):
    '''variable : ID'''

def p_variables(p):
    '''variables : variable 
                 | variable COMMA variables 
                 | empty'''

def p_modifier(p):
    '''modifier : access_modifier static_modifier
                | access_modifier
                | static_modifier
                | empty'''

def p_access_modifier(p):
    '''access_modifier  : PUBLIC 
                        | PRIVATE'''

def p_static_modifier(p):
    '''static_modifier  : STATIC'''

def p_type(p):
    '''type : INT 
            | FLOAT 
            | BOOLEAN 
            | ID'''

def p_type_with_void(p):
    '''type_with_void : type ID
                      | VOID ID'''

def p_formal_param(p):
    '''formal_param : type variable
                    | empty'''

def p_formals(p):
    '''formals  : formal_param 
                | formal_param COMMA formals'''

def p_block(p):
    '''block : LCURLY stmt_list RCURLY
             | LCURLY RCURLY'''

def p_stmt_list(p):
    '''stmt_list : stmt
                 | stmt_list stmt
    '''

def p_stmt(p):
    '''stmt : stmt_expr SEMICOLON
            | var_decl
            | block
            | for_stmt
            | if_stmt
            | while_stmt
            | do_stmt
            | CONTINUE SEMICOLON
            | BREAK SEMICOLON
            | RETURN expr SEMICOLON
            | SEMICOLON
    '''

def p_stmt_expr(p):
    '''stmt_expr    : method_invocation
                    | assign'''
def p_if_stmt(p):
    '''if_stmt  : IF LPAREN expr RPAREN stmt else_stmt'''

def p_else_stmt(p):
    '''else_stmt    : ELSE stmt
                    | empty'''

def p_while_stmt(p):
    '''while_stmt   : while_check stmt'''

def p_while_check(p):
    '''while_check  : WHILE LPAREN expr RPAREN'''

def p_do_stmt(p):
    '''do_stmt  : DO stmt while_check'''

def p_for_stmt(p):
    '''for_stmt : FOR LPAREN for_init SEMICOLON for_check SEMICOLON for_update RPAREN stmt'''

def p_for_init(p):
    '''for_init : stmt_expr
                | empty'''

def p_for_check(p):
    '''for_check    : expr
                    | empty'''

def p_for_update(p):
    '''for_update   : stmt_expr
                    | empty'''

def p_expr(p):
    '''expr : primary
            | unary_expr
            | binary_expr
            | comparison
            | assign
    '''
            # | new_array

def p_unary_expr(p):
    '''unary_expr : unary_op expr %prec UNARY'''
def p_binary_expr(p):
    '''binary_expr : expr plus_minus_op expr %prec PLUSMINUS
                   | expr times_divide_op expr %prec TIMESDIVIDE
                   | expr bool_op expr %prec BOOL
    '''

def p_primary(p):
    '''primary  : literal
                | lhs
                | method_invocation
                | LPAREN expr RPAREN
                | NEW ID LPAREN arguments RPAREN
                | THIS
                | SUPER
    '''

def p_literal(p):
    '''literal  : INTCONST
                | FLOATCONST
                | STRINGCONST
                | NULL
                | TRUE
                | FALSE
    '''

def p_lhs(p):
    '''lhs : field_access'''

def p_field_access(p):
    '''field_access : primary DOT ID 
                    | ID'''

def p_method_invocation(p):
    'method_invocation : field_access LPAREN arguments RPAREN'

def p_arguments(p):
    '''arguments : expr 
                 | expr COMMA arguments 
                 | empty'''

def p_assign(p):
    '''assign : lhs ASSIGN expr %prec ASSIGN
              | lhs PLUSPLUS
              | PLUSPLUS lhs
              | lhs MINUSMINUS
              | MINUSMINUS lhs'''
    
# def p_new_array(p):
#     '''new_array : NEW type arrays'''

# def p_arrays(p):
#     '''arrays   : array arrays
#                 | empty '''

# def p_array(p):
#     '''array    : LBRACKET expr RBRACKET
#                 | LBRACKET RBRACKET'''

def p_plus_minus_op(p):
    '''plus_minus_op : PLUS 
                     | MINUS'''

def p_times_divide_op(p):
    '''times_divide_op  : TIMES
                        | DIVIDE'''

def p_bool_op(p):
    '''bool_op  : AND
                | OR
                '''

def p_comparison(p):
    '''comparison : expr comp_op expr %prec COMP'''

def p_comp_op(p):
    '''comp_op  : EQUAL
                | NOTEQUAL
                | LT
                | GT
                | LEQ
                | GEQ'''

def p_unary_op(p):
    '''unary_op : PLUS 
                | MINUS
                | NOT'''

# Error rule for syntax errors
def p_error(p):
    if p:
        print("Syntax error: '%s' at line %d position %d" %(p.value, p.lineno, find_column(p.lexer.lexdata, p.lexer, value=p.value)))
    else:
        print("Syntax error at EOF")
    sys.exit()

# Build the parser
parser = yacc.yacc(debug=1)