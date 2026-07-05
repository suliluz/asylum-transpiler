import "std/string.asy";
import "std/sys.asy";

print("Testing divide by zero...\n");
let result: int = 0;
try {
    let x = 10;
    let y = 0;
    print("y is: ");
    print_num(y);
    print("\n");
    throw 1;
    print("This should not print!\n");
} catch (err) {
    print("Caught error code: ");
    print_num(err);
    print("\n");
    result = 255;
}

print("Execution continued! Result: ");
print_num(result);
print("\n");
