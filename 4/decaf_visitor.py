# Seungwon An (Harry), seunan, 115236174
# Andy (Yi Heng) Su, yihsu, 113378005

from decaf_ast import *

class NodeVisitor:
    def visit(self, node):
        # print(f'{type(self).__name__} VISITING {type(node).__name__}')
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        
        return visitor(node)

    def generic_visit(self, node):
        if not hasattr(node, 'children'): return

        for field_name in node.children:
            field_value = getattr(node, field_name, None)
            if isinstance(field_value, ASTNode):
                field_value.accept(self)
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, ASTNode):
                        item.accept(self)

class SymbolTableBuilder(NodeVisitor):
    def __init__(self, symbolTable):
        super().__init__()
        self.s = symbolTable
    
    def visit_Program(self, node):
        for _class in node.classes:
            node.result.append(_class.accept(self))
    
    def visit_ClassDecl(self, node):
        self.s.enter_class(node.name, node.super)
        node.class_body.accept(self)
        return self.s.exit_class()

    def visit_ClassBody(self, node):
        self.s.enter_block()
        for decl in node.decl_list:
            decl.accept(self)
        self.s.exit_block()

    def visit_FieldDecl(self, node):
        for variable in node.variables:
            self.s.add_field(variable, node.visibility, node.applicability, node.type)
    
    def visit_MethodDecl(self, node):
        self.s.set_formals(node.formals)
        node.body.accept(self)
        self.s.add_method(node.name, node.visibility, node.applicability, node.return_type, node.body)

    def visit_ConstructorDecl(self, node):
        if node.name != self.s.current_class['name']:
            print(f"Constructor name should be equal to the class name: {node.name} {self.s.current_class['name']}")
            exit(1)

        self.s.set_formals(node.formals)
        node.body.accept(self)
        self.s.add_constructor(node.visibility, node.body)
    
    def visit_VarDeclStmt(self, node):
        for variable in node.variables:
            self.s.add_variable(variable, 'local', node.type)
    
    def visit_BlockStmt(self, node):
        self.s.enter_block()
        for stmt in node.stmt_list:
            stmt.accept(self)
        self.s.exit_block()
    
    def visit_VarExpr(self, node):
        var_record = self.s.lookup_variable(node.variable_name)
        node.record = var_record
        node.id = var_record.get_id()

    def visit_IdRefExpr(self, node):
        if self.s.lookup_variable(node.id):
            node.node = VarExpr(node.id)
        elif self.s.lookup_class(node.id) or self.s.current_class['name'] == node.id:
            node.node = ClassRefExpr(node.id)
        else:
            print(f"ERROR: there is no matching variable or class name with id ({node.id})")
            exit(1)
        node.node.accept(self)
