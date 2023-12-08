# Seungwon An (Harry), seunan, 115236174
# Andy (Yi Heng) Su, yihsu, 113378005

import sys
from decaf_visitor import SymbolTableBuilder
from decaf_typecheck import TypeChecker
from decaf_ast import Symbol_Table

def find_column(input, token, **kwargs):
    start = 0
    value = kwargs.get('value', None)
    if value:
        start = token.lexpos - len(str(value))
    else:
        start = token.lexpos
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (start - line_start)

def main():
    fn = sys.argv[1] if len(sys.argv) > 1 else ""
    if fn == "":
        print("Missing file name for source program.")
        print("USAGE: python3 decaf_checker.py <decaf_source_file_name>")
        sys.exit()
    
    from decaf_lexer import lexer
    from decaf_parser import parser

    fh = open(fn, 'r')
    source = fh.read()
    fh.close()

    #Parse and Print
    result = parser.parse(source, lexer=lexer)
    symbolTable = Symbol_Table()
    symbolTableBuilder = SymbolTableBuilder(symbolTable)
    symbolTableBuilder.visit(result)

    #Type check
    typeChecker = TypeChecker(symbolTable)
    typeChecker.visit(result)

    print(result)

if __name__ == "__main__":
    main()
