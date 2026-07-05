import "std/ptr.asy";

func malloc(s0: byte, s1: byte, s2: byte, s3: byte) {
    _ptr_block[0] = 14;
    _ptr_block[1] = s0;
    _ptr_block[2] = s1;
    _ptr_block[3] = s2;
    _ptr_block[4] = s3;
    syscall(_ptr_block);
    // Address is returned in _ptr_block[5..8]
}

func free(a0: byte, a1: byte, a2: byte, a3: byte) {
    _ptr_block[0] = 15;
    _ptr_block[1] = a0;
    _ptr_block[2] = a1;
    _ptr_block[3] = a2;
    _ptr_block[4] = a3;
    syscall(_ptr_block);
}
