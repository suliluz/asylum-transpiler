import "std/sys.asy";

// 1. JSON Objects
let person = {
    "age": 25,
    "initial": 65
};

print("Person Initial: ");
print(person.initial);
print(10); // newline

// 2. Control flow & Operators
let sum = 0;
for (let i = 0; i != 5; i++) {
    sum += i;
}

print("Sum 0 to 4 (should be 10): ");
print_num(sum);
print(10);

// 3. Command Line Arguments
print("Command Line Argc: ");
print_num(argc);
print(10);

// 4. Arrays
let arr: int[3];
arr[0] = 72; // H
arr[1] = 105; // i
arr[2] = 33; // !

print("Array output: ");
print(arr[0]);
print(arr[1]);
print(arr[2]);
print(10);

// 5. While Loop & If/Else
let toggle = 1;
while (toggle != 0) {
    if (sum == 10) {
        print("Sum is correctly 10!\n");
    } else {
        print("Sum is wrong!\n");
    }
    toggle = 0;
}
