from parser import parse
ast = parse("let a: byte[10];")
print(ast.pretty())
