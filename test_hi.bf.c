#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define TAPE_SIZE 1048576

FILE* fd_table[256] = {NULL};
int sock_table[256] = {0};
unsigned char* tape_start = NULL;
unsigned int heap_ptr = TAPE_SIZE;

void handle_syscall(unsigned char* ptr) {
    unsigned char cmd = ptr[0];
    if (cmd == 1) {
        unsigned char mode = ptr[1];
        int valid = 0;
        for (int i = 2; ptr + i < tape_start + TAPE_SIZE; i++) {
            if (ptr[i] == '\0') { valid = 1; break; }
        }
        if (!valid) { ptr[0] = 0; return; }
        char* filename = (char*)(ptr + 2);
        const char* mode_str = (mode == 0) ? "r" : (mode == 1 ? "w" : "a");
        FILE* f = fopen(filename, mode_str);
        if (f) {
            int fd = 0;
            for (int i=1; i<256; i++) {
                if (!fd_table[i]) { fd = i; break; }
            }
            if (fd) {
                fd_table[fd] = f;
                ptr[0] = fd;
            } else {
                fclose(f);
                ptr[0] = 0;
            }
        } else {
            ptr[0] = 0;
        }
    } else if (cmd == 2) {
        int fd = ptr[1];
        int len = ptr[2];
        if (ptr + 1 + len > tape_start + TAPE_SIZE) {
            len = (tape_start + TAPE_SIZE) - (ptr + 1);
        }
        if (fd_table[fd] && len > 0) {
            int read_bytes = fread(ptr + 1, 1, len, fd_table[fd]);
            ptr[0] = read_bytes;
        } else {
            ptr[0] = 0;
        }
    } else if (cmd == 3) {
        int fd = ptr[1];
        int len = ptr[2];
        if (ptr + 3 + len > tape_start + TAPE_SIZE) {
            len = (tape_start + TAPE_SIZE) - (ptr + 3);
        }
        if (fd_table[fd] && len > 0) {
            int written = fwrite(ptr + 3, 1, len, fd_table[fd]);
            ptr[0] = written;
        } else {
            ptr[0] = 0;
        }
    } else if (cmd == 4) {
        int fd = ptr[1];
        if (fd_table[fd]) {
            fclose(fd_table[fd]);
            fd_table[fd] = NULL;
            ptr[0] = 0;
        } else {
            ptr[0] = 255;
        }
    } else if (cmd == 5) { // NET_SOCKET
        int s = socket(AF_INET, SOCK_STREAM, 0);
        if (s >= 0) {
            int opt = 1; setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
            int fd = 0;
            for (int i=1; i<256; i++) { if (!sock_table[i]) { fd = i; break; } }
            if (fd) { sock_table[fd] = s; ptr[0] = fd; } else { close(s); ptr[0] = 0; }
        } else { ptr[0] = 0; }
    } else if (cmd == 6) { // NET_BIND_LISTEN
        int fd = ptr[1];
        int port = (ptr[2] << 8) | ptr[3];
        if (sock_table[fd]) {
            struct sockaddr_in addr;
            addr.sin_family = AF_INET;
            addr.sin_addr.s_addr = INADDR_ANY;
            addr.sin_port = htons(port);
            if (bind(sock_table[fd], (struct sockaddr*)&addr, sizeof(addr)) == 0 && listen(sock_table[fd], 10) == 0) { ptr[0] = 1; } else { ptr[0] = 0; }
        } else { ptr[0] = 0; }
    } else if (cmd == 7) { // NET_ACCEPT
        int fd = ptr[1];
        if (sock_table[fd]) {
            int client = accept(sock_table[fd], NULL, NULL);
            if (client >= 0) {
                int new_fd = 0;
                for (int i=1; i<256; i++) { if (!sock_table[i]) { new_fd = i; break; } }
                if (new_fd) { sock_table[new_fd] = client; ptr[0] = new_fd; } else { close(client); ptr[0] = 0; }
            } else { ptr[0] = 0; }
        } else { ptr[0] = 0; }
    } else if (cmd == 8) { // NET_CONNECT
        int fd = ptr[1];
        int port = (ptr[2] << 8) | ptr[3];
        char* ip = (char*)(ptr + 4);
        if (sock_table[fd]) {
            struct sockaddr_in addr;
            addr.sin_family = AF_INET;
            addr.sin_port = htons(port);
            inet_pton(AF_INET, ip, &addr.sin_addr);
            if (connect(sock_table[fd], (struct sockaddr*)&addr, sizeof(addr)) == 0) { ptr[0] = 1; } else { ptr[0] = 0; }
        } else { ptr[0] = 0; }
    } else if (cmd == 9) { // NET_SEND
        int fd = ptr[1];
        int len = (ptr[2] << 8) | ptr[3];
        if (sock_table[fd] && len > 0) {
            int sent = send(sock_table[fd], ptr + 4, len, 0);
            ptr[0] = sent > 0 ? sent : 0;
        } else { ptr[0] = 0; }
    } else if (cmd == 10) { // NET_RECV
        int fd = ptr[1];
        int len = (ptr[2] << 8) | ptr[3];
        if (sock_table[fd] && len > 0) {
            int recvd = recv(sock_table[fd], ptr + 4, len, 0);
            if (recvd > 0) { ptr[0] = (recvd >> 8) & 0xFF; ptr[1] = recvd & 0xFF; } else { ptr[0] = 0; ptr[1] = 0; }
        } else { ptr[0] = 0; ptr[1] = 0; }
    } else if (cmd == 11) { // GFX_DRAW
        unsigned int addr = (ptr[1] << 24) | (ptr[2] << 16) | (ptr[3] << 8) | ptr[4];
        int width = ptr[5], height = ptr[6];
        printf("\033[H\033[2J"); // Clear screen
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                unsigned char r = tape_start[addr + (y * width + x) * 3];
                unsigned char g = tape_start[addr + (y * width + x) * 3 + 1];
                unsigned char b = tape_start[addr + (y * width + x) * 3 + 2];
                printf("\033[48;2;%d;%d;%dm  \033[0m", r, g, b);
            }
            printf("\n");
        }
        fflush(stdout);
    } else if (cmd == 12) { // READ_ADDR
        unsigned int addr = (ptr[1] << 24) | (ptr[2] << 16) | (ptr[3] << 8) | ptr[4];
        if (addr < TAPE_SIZE) { ptr[0] = tape_start[addr]; } else { ptr[0] = 0; }
    } else if (cmd == 13) { // WRITE_ADDR
        unsigned int addr = (ptr[1] << 24) | (ptr[2] << 16) | (ptr[3] << 8) | ptr[4];
        if (addr < TAPE_SIZE) { tape_start[addr] = ptr[5]; }
    } else if (cmd == 14) { // MALLOC
        unsigned int size = (ptr[1] << 24) | (ptr[2] << 16) | (ptr[3] << 8) | ptr[4];
        if (heap_ptr > 1024 + size) {
            heap_ptr -= size;
            ptr[5] = (heap_ptr >> 24) & 0xFF;
            ptr[6] = (heap_ptr >> 16) & 0xFF;
            ptr[7] = (heap_ptr >> 8) & 0xFF;
            ptr[8] = heap_ptr & 0xFF;
        } else { ptr[5] = ptr[6] = ptr[7] = ptr[8] = 0; }
    } else if (cmd == 15) { // FREE (noop bump allocator)
        ptr[0] = 1;
    } else if (cmd == 16) { // NET_CLOSE
        int fd = ptr[1];
        if (sock_table[fd]) { close(sock_table[fd]); sock_table[fd] = 0; ptr[0] = 1; } else { ptr[0] = 0; }
    } else if (cmd == 17) { // SYS_EXIT
        exit(ptr[1]);
    }
}

int main(int argc, char** argv) {
    unsigned char* tape = calloc(TAPE_SIZE, sizeof(unsigned char));
    tape_start = tape;
    unsigned char* ptr = tape + 1024;
    tape[0] = (unsigned char)argc;
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    tape[1] = (unsigned char)((tm.tm_year + 1900) % 100);
    tape[2] = (unsigned char)(tm.tm_mon + 1);
    tape[3] = (unsigned char)tm.tm_mday;
    tape[4] = (unsigned char)tm.tm_hour;
    tape[5] = (unsigned char)tm.tm_min;
    tape[6] = (unsigned char)tm.tm_sec;
    int offset = 7;
    for (int i = 0; i < argc; i++) {
        int len = strlen(argv[i]);
        if (offset + len + 1 >= 1024) break;
        strcpy((char*)(tape + offset), argv[i]);
        offset += len + 1;
    }

    ptr += 1; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    }
    ptr += 1; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    }
    (*ptr) += 1;
    ptr += 1; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    }
    ptr += 1; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    }
    ptr -= 1027; if (ptr < tape) ptr += TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    ptr += 1026; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    (*ptr) += 1;
    ptr += 1; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    (*ptr) += 1;
    ptr -= 1027; if (ptr < tape) ptr += TAPE_SIZE;
    }
    ptr += 1027; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    ptr -= 1027; if (ptr < tape) ptr += TAPE_SIZE;
    (*ptr) += 1;
    ptr += 1027; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    }
    ptr -= 1; if (ptr < tape) ptr += TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    ptr -= 1; if (ptr < tape) ptr += TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    }
    ptr += 1; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    }
    ptr -= 2; if (ptr < tape) ptr += TAPE_SIZE;
    while (*ptr) {
    ptr += 1; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    }
    (*ptr) += 104;
    putchar(*ptr); fflush(stdout);
    (*ptr) += 1;
    putchar(*ptr); fflush(stdout);
    (*ptr) -= 95;
    putchar(*ptr); fflush(stdout);
    while (*ptr) {
    (*ptr) -= 1;
    }
    ptr -= 1; if (ptr < tape) ptr += TAPE_SIZE;
    while (*ptr) {
    (*ptr) -= 1;
    }
    }
    free(tape);
    return 0;
}
