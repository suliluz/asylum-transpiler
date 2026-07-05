import "std/string.asy";
import "std/sys.asy";

let sum: int = 0;
for (let i = 0; i != 10; i++) {
    if (i == 3) {
        continue;
    }
    if (i == 7) {
        break;
    }
    sum += i;
}
// Sum should be 0 + 1 + 2 + 4 + 5 + 6 = 18
print("Sum is: ");
print_num(sum);
print("\n");
