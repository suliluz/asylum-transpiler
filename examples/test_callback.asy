import "std/sys.asy";

func add(a: byte, b: byte) byte {
    return a + b;
}

func sub(a: byte, b: byte) byte {
    return a - b;
}

func run_math(op_func: byte, x: byte, y: byte) byte {
    return op_func(x, y);
}

let cb1 = add;
let cb2 = sub;

print("Add 5 + 3: ");
print_num(run_math(cb1, 5, 3));
print("\n");

print("Sub 10 - 4: ");
print_num(run_math(cb2, 10, 4));
print("\n");
