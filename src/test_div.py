from parser import parse
from generator import Generator

ast = parse("func main() { let x = 10; let y = 0; let res = x / y; } main();")
gen = Generator()
gen.visit(ast)
print(gen.code.count('#'))
