from parser import parse
from generator import Generator

source = r"""
func main() {
    let x = 10;
    let y = 0;
    let res = x / y;
    print("THIS SHOULD BE SKIPPED\n");
}
main();
"""
ast = parse(source)
gen = Generator()

original_alloc_temp = gen.mem.alloc_temp
def logging_alloc_temp():
    addr = original_alloc_temp()
    print("Allocated temp:", addr)
    return addr

gen.mem.alloc_temp = logging_alloc_temp
gen.visit(ast)
