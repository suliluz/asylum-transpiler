// Asylum Networking Standard Library

let _net_block @ 522 : byte[16];

func net_socket() {
    _net_block[0] = 5;
    syscall(_net_block);
    return _net_block[0];
}

func net_bind_listen(fd: byte, port_high: byte, port_low: byte) {
    _net_block[0] = 6;
    _net_block[1] = fd;
    _net_block[2] = port_high;
    _net_block[3] = port_low;
    syscall(_net_block);
    return _net_block[0];
}

func net_accept(fd: byte) {
    _net_block[0] = 7;
    _net_block[1] = fd;
    syscall(_net_block);
    return _net_block[0];
}

func net_connect(fd: byte, port_high: byte, port_low: byte) {
    _net_block[0] = 8;
    _net_block[1] = fd;
    _net_block[2] = port_high;
    _net_block[3] = port_low;
    // IP must be written to _net_block[4...] before calling
    syscall(_net_block);
    return _net_block[0];
}

func net_send(fd: byte, len_high: byte, len_low: byte) {
    _net_block[0] = 9;
    _net_block[1] = fd;
    _net_block[2] = len_high;
    _net_block[3] = len_low;
    // Data must be written to _net_block[4...] before calling
    syscall(_net_block);
    return _net_block[0];
}

func net_recv(fd: byte, len_high: byte, len_low: byte) {
    _net_block[0] = 10;
    _net_block[1] = fd;
    _net_block[2] = len_high;
    _net_block[3] = len_low;
    syscall(_net_block);
    // Bytes read is returned in _net_block[0] (high) and _net_block[1] (low).
    // Data is populated in _net_block[4...]
}

func net_close(fd: byte) {
    _net_block[0] = 16;
    _net_block[1] = fd;
    syscall(_net_block);
    return _net_block[0];
}
