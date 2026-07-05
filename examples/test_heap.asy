import "std/mem.asy";
import "std/string.asy";

// Allocate 20 bytes
malloc(0, 0, 0, 20);

// We know malloc puts the pointer in _ptr_block[5..8]. 
// So let's write "Hi" to that pointer.
let p0 = _ptr_block[5];
let p1 = _ptr_block[6];
let p2 = _ptr_block[7];
let p3 = _ptr_block[8];

write_ptr(p0, p1, p2, p3, 72); // 'H'
inc_current_ptr();
write_current_ptr(105); // 'i'
inc_current_ptr();
write_current_ptr(10); // '\n'
inc_current_ptr();
write_current_ptr(0); // '\0'

print_str_ptr(p0, p1, p2, p3);

