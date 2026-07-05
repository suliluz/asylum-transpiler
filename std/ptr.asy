// Asylum Pointers Standard Library

let _ptr_block @ 512 : byte[10];

func read_ptr(a0: byte, a1: byte, a2: byte, a3: byte) {
    _ptr_block[0] = 12;
    _ptr_block[1] = a0;
    _ptr_block[2] = a1;
    _ptr_block[3] = a2;
    _ptr_block[4] = a3;
    syscall(_ptr_block);
    return _ptr_block[0];
}

func write_ptr(a0: byte, a1: byte, a2: byte, a3: byte, val: byte) {
    _ptr_block[0] = 13;
    _ptr_block[1] = a0;
    _ptr_block[2] = a1;
    _ptr_block[3] = a2;
    _ptr_block[4] = a3;
    _ptr_block[5] = val;
    syscall(_ptr_block);
}

func read_current_ptr() {
    _ptr_block[0] = 12;
    syscall(_ptr_block);
    return _ptr_block[0];
}

func write_current_ptr(val: byte) {
    _ptr_block[0] = 13;
    _ptr_block[5] = val;
    syscall(_ptr_block);
}

func inc_current_ptr() {
    let t4 = _ptr_block[4];
    t4++;
    _ptr_block[4] = t4;
    
    if (t4 == 0) {
        let t3 = _ptr_block[3];
        t3++;
        _ptr_block[3] = t3;
        
        if (t3 == 0) {
            let t2 = _ptr_block[2];
            t2++;
            _ptr_block[2] = t2;
            
            if (t2 == 0) {
                let t1 = _ptr_block[1];
                t1++;
                _ptr_block[1] = t1;
            }
        }
    }
}
