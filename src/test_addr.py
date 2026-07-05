from parser import parse
from generator import Generator

source = """
func main() {
    let x = 10;
    let y = 0;
    let result = x / y;
}
main();
"""
ast = parse(source)
gen = Generator()
gen.visit(ast)
print("x addr:", gen.mem.get("x"))
print("y addr:", gen.mem.get("y"))
