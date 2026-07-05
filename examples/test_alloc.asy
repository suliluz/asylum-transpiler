let x = 10;
let y = 20;
let sum = 0;
sum += x;
sum += y;
import "std/sys.asy";
print_digit(sum); // wait, print_digit prints (sum+48), so if sum is 30, it prints something else.
