import "std/string.asy";
import "std/sys.asy";

let a: int = 10;
let b: int = 3;
let c: int = 2;

// PEMDAS: 10 + 3 * 2 ^ 3 - 10 / 2 = 10 + 3 * 8 - 5 = 10 + 24 - 5 = 29
let res: int = a + b * c ^ 3 - a / c;
print("PEMDAS result is: ");
print_num(res);
print("\n");

// Modulo: 10 % 3 = 1
let rem: int = a % b;
print("Modulo result is: ");
print_num(rem);
print("\n");
