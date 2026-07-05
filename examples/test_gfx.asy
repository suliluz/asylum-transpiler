import "std/gfx.asy";

let fb : byte[300]; // 10x10 RGB = 300 bytes

// We'll map fb to addr 1024 manually for simplicity of calculating pointer
let fb_0 = 0; let fb_1 = 0; let fb_2 = 4; let fb_3 = 0; // 1024 = 0x0400 -> fb_2=4, fb_3=0

func draw() {
    let r = 255;
    let g = 0;
    let b = 100;
    
    // Fill 100 pixels
    let i = 0;
    while (i != 100) {
        // We can't index easily dynamically yet, so let's just color the first 30 bytes for testing
        i++;
    
    
    fb[0] = 255; fb[1] = 0; fb[2] = 0; // Red
    fb[3] = 0; fb[4] = 255; fb[5] = 0; // Green
    fb[6] = 0; fb[7] = 0; fb[8] = 255; // Blue
    fb[9] = 255; fb[10] = 255; fb[11] = 255; // White
    
    render_frame(fb_0, fb_1, fb_2, fb_3, 10, 1);


draw();
