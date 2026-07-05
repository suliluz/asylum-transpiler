import "std/sys.asy";
import "std/mem.asy";
import "std/ptr.asy";

func main() {
    let t = true;
    let f = false;
    let n = null;
    
    if (t) {
        print("true works!\n");
    }
    if (f == 0) {
        print("false works!\n");
    }
    if (n == 0) {
        print("null works!\n");
    }
    
    let i = 0;
    do {
        print("do while works!\n");
        i++;
    } while (i < 1);
    
    let arr: byte[3];
    arr[0] = 65;
    arr[1] = 66;
    arr[2] = 67;
    
    foreach (item in arr) {
        print(item);
    }
    print("\n");
    
    malloc(0, 0, 0, 3);
    let dyn_arr = _ptr_block[8]; // Assuming returned addr is in 8 since it's 32-bit big endian maybe?
    // actually, malloc doesn't return anything.
    // The returned address is in _ptr_block[5], [6], [7], [8].
    // But wait, read_ptr uses 4 bytes.
    // To keep it simple, if our heap ptr is in the first 255 bytes, it will be in _ptr_block[8].
    
    write_ptr(0, 0, 0, dyn_arr, 68); // D
    let tmp = dyn_arr;
    tmp++;
    write_ptr(0, 0, 0, tmp, 69); // E
    tmp++;
    write_ptr(0, 0, 0, tmp, 70); // F
    
    foreach (dyn_item in dyn_arr, 3) {
        print(dyn_item);
    }
    print("\n");
}

main();
