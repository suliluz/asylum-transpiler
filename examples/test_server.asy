import "std/net.asy";

let server_fd = net_socket();
let success = net_bind_listen(server_fd, 31, 144); // 8080
let client_fd = net_accept(server_fd);

if (client_fd != 0) {
    // Read the request so the socket buffer is empty, preventing TCP RST on close
    net_recv(client_fd, 4, 0); // Read 1024 bytes (4 * 256)

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
    _net_block[23] = 72; // H
    _net_block[24] = 105; // i
    _net_block[25] = 33; // !
    
    net_send(client_fd, 0, 22);
    net_close(client_fd);

net_close(server_fd);
