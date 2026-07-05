import "std/ptr.asy";

func print_str_ptr(a0: byte, a1: byte, a2: byte, a3: byte) {
    let c = read_ptr(a0, a1, a2, a3);
    while (c != 0) {
        print(c);
        inc_current_ptr();
        c = read_current_ptr();
    }
}
