# Seungwon An (Harry), seunan, 115236174
# Andy (Yi Heng) Su, yihsu, 113378005

import sys
import ply.lex as lex
from decaf_compiler import find_column

#Possible Tokens
tokens = [
    'ID',
    'PLUS',
    'PLUSPLUS',
    'MINUS',
    'MINUSMINUS',
    'TIMES',
    'DIVIDE',
    'MODULUS',
    'LPAREN',
    'RPAREN',
    'INTCONST',
    'FLOATCONST',
    'STRINGCONST',
    'LCURLY',
    'RCURLY',
    'DOT',
    'SEMICOLON',
    "ASSIGN",
    "COMMA",
    "NOT",
    "AND",
    "OR",
    "EQUAL",
    "NOTEQUAL",
    "LT",
    "GT",
    "LEQ",
    "GEQ"
]

reserved = {
    'boolean': 'BOOLEAN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'class': 'CLASS',
    'else': 'ELSE',
    'extends': 'EXTENDS',
    'false': 'FALSE',
    'float': 'FLOAT',
    'for': 'FOR',
    'if': 'IF',
    'int': 'INT',
    'new': 'NEW',
    'null': 'NULL',
    'private': 'PRIVATE',
    'public': 'PUBLIC',
    'return': 'RETURN',
    'static': 'STATIC',
    'super': 'SUPER',
    'this': 'THIS',
    'true': 'TRUE',
    'void': 'VOID',
    'while': 'WHILE',
}

tokens = tokens + list(reserved.values())

t_PLUS = r'\+'
t_PLUSPLUS = r'\+\+'
t_MINUS = r'-'
t_MINUSMINUS = r'--'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULUS = r'%'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURLY = r'{'
t_RCURLY = r'}'
t_DOT = r'\.'
t_SEMICOLON = r';'
t_ASSIGN = r'='
t_COMMA = r','
t_AND = r'&&'
t_OR = r'\|\|'
t_EQUAL = r'=='
t_NOTEQUAL = r'!='
t_LT = r'<'
t_GT = r'>'
t_LEQ = r'<='
t_GEQ = r'>='
t_NOT = r'!'

t_ignore  = ' \t'
t_ignore_COMMENT = r'\/\*[\s\S]*?\*\/|\/\/.*'

def t_ID(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_FLOATCONST(t):
    r'\d+\.\d+'  #accounts for all floats in decaf.pdf
    t.value = float(t.value)
    return t

def t_INTCONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRINGCONST(t):
    r'"([^\\"]|\\.)*"'
    t.value = t.value[1:-1]
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Lexer error: '%s' at line %d position %d" % (str(t.value[0]), t.lexer.lineno, find_column(t.lexer.lexdata, t.lexer)))
    sys.exit()

lexer = lex.lex()