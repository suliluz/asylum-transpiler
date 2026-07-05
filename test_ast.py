from parser import parse
ast = parse('for (let s = 0; s != spaces; s++) { print(space_char); }')
print(ast.pretty())
