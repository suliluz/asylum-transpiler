let _sys_time_block @ 510 : byte[5]; // Allocate some space for time syscall

// Returns a 32-bit unsigned integer (array of 4 bytes)
// We return the raw pointer to the block, user can read 4 bytes.
// Or we just return the lowest 8 bits as a byte for simple uses?
// Actually, since functions can only return 1 byte, we'll return a pointer to the 4 bytes.

func sys_millis() {
    _sys_time_block[0] = 17; // SYS_MILLIS
    syscall(_sys_time_block);
}
