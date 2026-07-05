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

import re
bf = gen.code
try_idx = "".join(bf).find('#')
print("Hash at index:", try_idx)
