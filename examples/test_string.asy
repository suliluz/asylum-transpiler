import "std/string.asy";

let str_addr0 = 0;
let str_addr1 = 0;
let str_addr2 = 4;
let str_addr3 = 4; // 1028

let s : byte[10] = "Hello\n";
print_str_ptr(str_addr0, str_addr1, str_addr2, str_addr3);
