import "std/sys.asy";
import "std/math.asy";

print("Testing Math Standard Library\n");

// 1. Min / Max
let a = 15;
let b = 25;
print("Min of 15 and 25: ");
print_num(min(a, b));
print(10);
print("Max of 15 and 25: ");
print_num(max(a, b));
print(10);

// 2. Mul
let c = 6;
let d = 7;
print("Mul of 6 and 7: ");
print_num(mul(c, d));
print(10);

// 3. Div / Mod
let num = 100;
let div_by = 3;
print("Div 100 by 3: ");
print_num(div(num, div_by));
print(10);

print("Mod 100 by 3: ");
print_num(mod(num, div_by));
print(10);

// 4. Pow
let base = 2;
let exp = 5;
print("Pow 2 to 5: ");
print_num(pow(base, exp));
print(10);

// 5. Abs
let neg = 0;
neg -= 42; // -42 wraps around to 214
print("Abs of -42 (raw byte value ");
print_num(neg);
print("): ");
print_num(abs(neg));
print(10);

let pos = 42;
print("Abs of 42: ");
print_num(abs(pos));
print(10);
