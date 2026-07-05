import "std/sys.asy";
import "std/math.asy";
import "std/gfx.asy";
import "std/net.asy";
import "std/mem.asy";
import "std/ptr.asy";
import "std/string.asy";

// ==========================================
// 1. Graphics: Render a Startup Logo
// ==========================================
print("Allocating 150 bytes for 10x5 RGB Framebuffer...\n");
malloc(0, 0, 0, 150); // 10 * 5 * 3 = 150
let f0 = _ptr_block[5];
let f1 = _ptr_block[6];
let f2 = _ptr_block[7];
let f3 = _ptr_block[8];

for (let y = 0; y != 5; y++) {
    for (let x = 0; x != 10; x++) {
        let offset = mul(y, 10);
        let final_off = offset;
        final_off += x;
        let remainder = mod(final_off, 2);
        
        if (remainder == 0) {
            write_ptr(f0, f1, f2, f3, 0); inc_current_ptr(); // R
            write_ptr(f0, f1, f2, f3, 255); inc_current_ptr(); // G
            write_ptr(f0, f1, f2, f3, 0); inc_current_ptr(); // B
        } else {
            write_ptr(f0, f1, f2, f3, 0); inc_current_ptr(); // R
            write_ptr(f0, f1, f2, f3, 0); inc_current_ptr(); // G
            write_ptr(f0, f1, f2, f3, 0); inc_current_ptr(); // B
        }
    }
}
print("Rendering Asylum Startup Logo (10x5):\n");
render_frame(f0, f1, f2, f3, 10, 5);
print(10); // Newline


// ==========================================
// 2. Dynamic Memory & Pointers
// ==========================================
print("Allocating dynamic memory...\n");
malloc(0, 0, 0, 32); // Allocate 32 bytes

// Extract the 32-bit pointer returned by malloc
let p0 = _ptr_block[5];
let p1 = _ptr_block[6];
let p2 = _ptr_block[7];
let p3 = _ptr_block[8];

// Write a custom message dynamically to the heap via pointers
// "Hello from Heap!"
let temp_val = 0;

temp_val = 72;  write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // H
temp_val = 101; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // e
temp_val = 108; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // l
temp_val = 108; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // l
temp_val = 111; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // o
temp_val = 32;  write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); //  
temp_val = 102; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // f
temp_val = 114; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // r
temp_val = 111; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // o
temp_val = 109; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // m
temp_val = 32;  write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); //  
temp_val = 72;  write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // H
temp_val = 101; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // e
temp_val = 97;  write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // a
temp_val = 112; write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // p
temp_val = 33;  write_ptr(p0, p1, p2, p3, temp_val); inc_current_ptr(); // !
temp_val = 0;   write_ptr(p0, p1, p2, p3, temp_val); // \0 Null Terminator

print("Reading from Heap: ");
print_str_ptr(p0, p1, p2, p3);
print(10); // Newline


// ==========================================
// 3. Networking: Booting up TCP Web Server
// ==========================================
print("Booting Web Server on Port 8080...\n");
let server_fd = net_socket();
let success = net_bind_listen(server_fd, 31, 144); // 8080 = (31 * 256) + 144

if (success != 0) {
    print("Listening... run: curl http://localhost:8080\n");
    let loop = 1;
    
    // We only process one request before shutting down gracefully
    while (loop == 1) {
        let client_fd = net_accept(server_fd);
        
        if (client_fd != 0) {
            print("Received client connection!\n");
            
            // Read incoming HTTP request (flush buffer)
            net_recv(client_fd, 4, 0); // Read 1024 bytes (4 * 256)
            
            // Write HTTP Response headers
            _net_block[4] = 72; // H
            _net_block[5] = 84; // T
            _net_block[6] = 84; // T
            _net_block[7] = 80; // P
            _net_block[8] = 47; // /
            _net_block[9] = 49; // 1
            _net_block[10] = 46; // .
            _net_block[11] = 49; // 1
            _net_block[12] = 32; //  
            _net_block[13] = 50; // 2
            _net_block[14] = 48; // 0
            _net_block[15] = 48; // 0
            _net_block[16] = 32; //  
            _net_block[17] = 79; // O
            _net_block[18] = 75; // K
            _net_block[19] = 13; // \r
            _net_block[20] = 10; // \n
            _net_block[21] = 13; // \r
            _net_block[22] = 10; // \n
            
            // Write HTTP Body
            _net_block[23] = 65; // A
            _net_block[24] = 115; // s
            _net_block[25] = 121; // y
            _net_block[26] = 108; // l
            _net_block[27] = 117; // u
            _net_block[28] = 109; // m
            _net_block[29] = 32; //  
            _net_block[30] = 82; // R
            _net_block[31] = 111; // o
            _net_block[32] = 99; // c
            _net_block[33] = 107; // k
            _net_block[34] = 115; // s
            _net_block[35] = 33; // !
            _net_block[36] = 10; // \n
            
            net_send(client_fd, 0, 33);
            net_close(client_fd);
            
            print("Successfully handled client! Shutting down server.\n");
            loop = 0; // Break the while loop
        }
    }
} else {
    print("Failed to bind server on 8080.\n");
}

net_close(server_fd);
print("Exiting.\n");
