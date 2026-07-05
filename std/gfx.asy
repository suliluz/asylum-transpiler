// Asylum Terminal Graphics Standard Library

let _gfx_block @ 550 : byte[7];

func render_frame(addr0: byte, addr1: byte, addr2: byte, addr3: byte, width: byte, height: byte) {
    _gfx_block[0] = 11;
    _gfx_block[1] = addr0;
    _gfx_block[2] = addr1;
    _gfx_block[3] = addr2;
    _gfx_block[4] = addr3;
    _gfx_block[5] = width;
    _gfx_block[6] = height;
    syscall(_gfx_block);
}
