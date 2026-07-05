import "std/sys.asy";
let sum: byte = 0;
let i: byte = 0;
while (i != 5) {
    print("Loop iteration...\n");
    sum += 1;
    i++;
}
if (sum == 5) {
    print("Loop works!\n");
} else {
    print("Loop failed!\n");
}
