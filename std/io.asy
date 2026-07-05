// Asylum Standard I/O Library

let io_block @ 10 : byte[256];

func fopen(mode: byte) {
    io_block[0] = 1; // CMD: OPEN
    io_block[1] = mode; // 0=Read, 1=Write, 2=Append
    // The filename MUST be set at io_block[2...] BEFORE calling fopen
    syscall(io_block);
    return io_block[0];
}

func fread(fd: byte, len: byte) {
    io_block[0] = 2; // CMD: READ
    io_block[1] = fd;
    io_block[2] = len;
    syscall(io_block);
    return io_block[0];
}

func fwrite(fd: byte, len: byte) {
    io_block[0] = 3; // CMD: WRITE
    io_block[1] = fd;
    io_block[2] = len;
    // The data MUST be set at io_block[3...] BEFORE calling fwrite
    syscall(io_block);
    return io_block[0];
}

func fclose(fd: byte) {
    io_block[0] = 4; // CMD: CLOSE
    io_block[1] = fd;
    syscall(io_block);
    return io_block[0];
}
