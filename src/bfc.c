#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void compile_bf_to_c(const char* bf_code, FILE* out) {
    fprintf(out, "#include <stdio.h>\n");
    fprintf(out, "#include <stdlib.h>\n");
    fprintf(out, "#include <string.h>\n");
    fprintf(out, "#include <time.h>\n");
    fprintf(out, "#include <unistd.h>\n");
    fprintf(out, "#include <sys/socket.h>\n");
    fprintf(out, "#include <netinet/in.h>\n");
    fprintf(out, "#include <arpa/inet.h>\n\n");
    fprintf(out, "#define TAPE_SIZE 1048576\n\n");
    fprintf(out, "FILE* fd_table[256] = {NULL};\n");
    fprintf(out, "int sock_table[256] = {0};\n");
    fprintf(out, "unsigned char* tape_start = NULL;\n");
    fprintf(out, "unsigned int heap_ptr = TAPE_SIZE;\n\n");
    fprintf(out, "void handle_syscall(unsigned char* ptr) {\n");
    fprintf(out, "    unsigned char cmd = ptr[0];\n");
    fprintf(out, "    if (cmd == 1) {\n");
    fprintf(out, "        unsigned char mode = ptr[1];\n");
    fprintf(out, "        int valid = 0;\n");
    fprintf(out, "        for (int i = 2; ptr + i < tape_start + TAPE_SIZE; i++) {\n");
    fprintf(out, "            if (ptr[i] == '\\0') { valid = 1; break; }\n");
    fprintf(out, "        }\n");
    fprintf(out, "        if (!valid) { ptr[0] = 0; return; }\n");
    fprintf(out, "        char* filename = (char*)(ptr + 2);\n");
    fprintf(out, "        const char* mode_str = (mode == 0) ? \"r\" : (mode == 1 ? \"w\" : \"a\");\n");
    fprintf(out, "        FILE* f = fopen(filename, mode_str);\n");
    fprintf(out, "        if (f) {\n");
    fprintf(out, "            int fd = 0;\n");
    fprintf(out, "            for (int i=1; i<256; i++) {\n");
    fprintf(out, "                if (!fd_table[i]) { fd = i; break; }\n");
    fprintf(out, "            }\n");
    fprintf(out, "            if (fd) {\n");
    fprintf(out, "                fd_table[fd] = f;\n");
    fprintf(out, "                ptr[0] = fd;\n");
    fprintf(out, "            } else {\n");
    fprintf(out, "                fclose(f);\n");
    fprintf(out, "                ptr[0] = 0;\n");
    fprintf(out, "            }\n");
    fprintf(out, "        } else {\n");
    fprintf(out, "            ptr[0] = 0;\n");
    fprintf(out, "        }\n");
    fprintf(out, "    } else if (cmd == 2) {\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        int len = ptr[2];\n");
    fprintf(out, "        if (ptr + 1 + len > tape_start + TAPE_SIZE) {\n");
    fprintf(out, "            len = (tape_start + TAPE_SIZE) - (ptr + 1);\n");
    fprintf(out, "        }\n");
    fprintf(out, "        if (fd_table[fd] && len > 0) {\n");
    fprintf(out, "            int read_bytes = fread(ptr + 1, 1, len, fd_table[fd]);\n");
    fprintf(out, "            ptr[0] = read_bytes;\n");
    fprintf(out, "        } else {\n");
    fprintf(out, "            ptr[0] = 0;\n");
    fprintf(out, "        }\n");
    fprintf(out, "    } else if (cmd == 3) {\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        int len = ptr[2];\n");
    fprintf(out, "        if (ptr + 3 + len > tape_start + TAPE_SIZE) {\n");
    fprintf(out, "            len = (tape_start + TAPE_SIZE) - (ptr + 3);\n");
    fprintf(out, "        }\n");
    fprintf(out, "        if (fd_table[fd] && len > 0) {\n");
    fprintf(out, "            int written = fwrite(ptr + 3, 1, len, fd_table[fd]);\n");
    fprintf(out, "            ptr[0] = written;\n");
    fprintf(out, "        } else {\n");
    fprintf(out, "            ptr[0] = 0;\n");
    fprintf(out, "        }\n");
    fprintf(out, "    } else if (cmd == 4) {\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        if (fd_table[fd]) {\n");
    fprintf(out, "            fclose(fd_table[fd]);\n");
    fprintf(out, "            fd_table[fd] = NULL;\n");
    fprintf(out, "            ptr[0] = 0;\n");
    fprintf(out, "        } else {\n");
    fprintf(out, "            ptr[0] = 255;\n");
    fprintf(out, "        }\n");
    fprintf(out, "    } else if (cmd == 5) { // NET_SOCKET\n");
    fprintf(out, "        int s = socket(AF_INET, SOCK_STREAM, 0);\n");
    fprintf(out, "        if (s >= 0) {\n");
    fprintf(out, "            int opt = 1; setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));\n");
    fprintf(out, "            int fd = 0;\n");
    fprintf(out, "            for (int i=1; i<256; i++) { if (!sock_table[i]) { fd = i; break; } }\n");
    fprintf(out, "            if (fd) { sock_table[fd] = s; ptr[0] = fd; } else { close(s); ptr[0] = 0; }\n");
    fprintf(out, "        } else { ptr[0] = 0; }\n");
    fprintf(out, "    } else if (cmd == 6) { // NET_BIND_LISTEN\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        int port = (ptr[2] << 8) | ptr[3];\n");
    fprintf(out, "        if (sock_table[fd]) {\n");
    fprintf(out, "            struct sockaddr_in addr;\n");
    fprintf(out, "            addr.sin_family = AF_INET;\n");
    fprintf(out, "            addr.sin_addr.s_addr = INADDR_ANY;\n");
    fprintf(out, "            addr.sin_port = htons(port);\n");
    fprintf(out, "            if (bind(sock_table[fd], (struct sockaddr*)&addr, sizeof(addr)) == 0 && listen(sock_table[fd], 10) == 0) { ptr[0] = 1; } else { ptr[0] = 0; }\n");
    fprintf(out, "        } else { ptr[0] = 0; }\n");
    fprintf(out, "    } else if (cmd == 7) { // NET_ACCEPT\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        if (sock_table[fd]) {\n");
    fprintf(out, "            int client = accept(sock_table[fd], NULL, NULL);\n");
    fprintf(out, "            if (client >= 0) {\n");
    fprintf(out, "                int new_fd = 0;\n");
    fprintf(out, "                for (int i=1; i<256; i++) { if (!sock_table[i]) { new_fd = i; break; } }\n");
    fprintf(out, "                if (new_fd) { sock_table[new_fd] = client; ptr[0] = new_fd; } else { close(client); ptr[0] = 0; }\n");
    fprintf(out, "            } else { ptr[0] = 0; }\n");
    fprintf(out, "        } else { ptr[0] = 0; }\n");
    fprintf(out, "    } else if (cmd == 8) { // NET_CONNECT\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        int port = (ptr[2] << 8) | ptr[3];\n");
    fprintf(out, "        char* ip = (char*)(ptr + 4);\n");
    fprintf(out, "        if (sock_table[fd]) {\n");
    fprintf(out, "            struct sockaddr_in addr;\n");
    fprintf(out, "            addr.sin_family = AF_INET;\n");
    fprintf(out, "            addr.sin_port = htons(port);\n");
    fprintf(out, "            inet_pton(AF_INET, ip, &addr.sin_addr);\n");
    fprintf(out, "            if (connect(sock_table[fd], (struct sockaddr*)&addr, sizeof(addr)) == 0) { ptr[0] = 1; } else { ptr[0] = 0; }\n");
    fprintf(out, "        } else { ptr[0] = 0; }\n");
    fprintf(out, "    } else if (cmd == 9) { // NET_SEND\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        int len = (ptr[2] << 8) | ptr[3];\n");
    fprintf(out, "        if (sock_table[fd] && len > 0) {\n");
    fprintf(out, "            int sent = send(sock_table[fd], ptr + 4, len, 0);\n");
    fprintf(out, "            ptr[0] = sent > 0 ? sent : 0;\n");
    fprintf(out, "        } else { ptr[0] = 0; }\n");
    fprintf(out, "    } else if (cmd == 10) { // NET_RECV\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        int len = (ptr[2] << 8) | ptr[3];\n");
    fprintf(out, "        if (sock_table[fd] && len > 0) {\n");
    fprintf(out, "            int recvd = recv(sock_table[fd], ptr + 4, len, 0);\n");
    fprintf(out, "            if (recvd > 0) { ptr[0] = (recvd >> 8) & 0xFF; ptr[1] = recvd & 0xFF; } else { ptr[0] = 0; ptr[1] = 0; }\n");
    fprintf(out, "        } else { ptr[0] = 0; ptr[1] = 0; }\n");
    fprintf(out, "    } else if (cmd == 11) { // GFX_DRAW\n");
    fprintf(out, "        unsigned int addr = (ptr[1] << 24) | (ptr[2] << 16) | (ptr[3] << 8) | ptr[4];\n");
    fprintf(out, "        int width = ptr[5], height = ptr[6];\n");
    fprintf(out, "        printf(\"\\033[H\\033[2J\"); // Clear screen\n");
    fprintf(out, "        for (int y = 0; y < height; y++) {\n");
    fprintf(out, "            for (int x = 0; x < width; x++) {\n");
    fprintf(out, "                unsigned char r = tape_start[addr + (y * width + x) * 3];\n");
    fprintf(out, "                unsigned char g = tape_start[addr + (y * width + x) * 3 + 1];\n");
    fprintf(out, "                unsigned char b = tape_start[addr + (y * width + x) * 3 + 2];\n");
    fprintf(out, "                printf(\"\\033[48;2;%%d;%%d;%%dm  \\033[0m\", r, g, b);\n");
    fprintf(out, "            }\n");
    fprintf(out, "            printf(\"\\n\");\n");
    fprintf(out, "        }\n");
    fprintf(out, "        fflush(stdout);\n");
    fprintf(out, "    } else if (cmd == 12) { // READ_ADDR\n");
    fprintf(out, "        unsigned int addr = (ptr[1] << 24) | (ptr[2] << 16) | (ptr[3] << 8) | ptr[4];\n");
    fprintf(out, "        if (addr < TAPE_SIZE) { ptr[0] = tape_start[addr]; } else { ptr[0] = 0; }\n");
    fprintf(out, "    } else if (cmd == 13) { // WRITE_ADDR\n");
    fprintf(out, "        unsigned int addr = (ptr[1] << 24) | (ptr[2] << 16) | (ptr[3] << 8) | ptr[4];\n");
    fprintf(out, "        if (addr < TAPE_SIZE) { tape_start[addr] = ptr[5]; }\n");
    fprintf(out, "    } else if (cmd == 14) { // MALLOC\n");
    fprintf(out, "        unsigned int size = (ptr[1] << 24) | (ptr[2] << 16) | (ptr[3] << 8) | ptr[4];\n");
    fprintf(out, "        if (heap_ptr > 1024 + size) {\n");
    fprintf(out, "            heap_ptr -= size;\n");
    fprintf(out, "            ptr[5] = (heap_ptr >> 24) & 0xFF;\n");
    fprintf(out, "            ptr[6] = (heap_ptr >> 16) & 0xFF;\n");
    fprintf(out, "            ptr[7] = (heap_ptr >> 8) & 0xFF;\n");
    fprintf(out, "            ptr[8] = heap_ptr & 0xFF;\n");
    fprintf(out, "        } else { ptr[5] = ptr[6] = ptr[7] = ptr[8] = 0; }\n");
    fprintf(out, "    } else if (cmd == 15) { // FREE (noop bump allocator)\n");
    fprintf(out, "        ptr[0] = 1;\n");
    fprintf(out, "    } else if (cmd == 16) { // NET_CLOSE\n");
    fprintf(out, "        int fd = ptr[1];\n");
    fprintf(out, "        if (sock_table[fd]) { close(sock_table[fd]); sock_table[fd] = 0; ptr[0] = 1; } else { ptr[0] = 0; }\n");
    fprintf(out, "    }\n");
    fprintf(out, "}\n\n");
    
    fprintf(out, "int main(int argc, char** argv) {\n");
    fprintf(out, "    unsigned char* tape = calloc(TAPE_SIZE, sizeof(unsigned char));\n");
    fprintf(out, "    tape_start = tape;\n");
    fprintf(out, "    unsigned char* ptr = tape + 1024;\n");
    fprintf(out, "    tape[10] = (unsigned char)argc;\n");
    fprintf(out, "    time_t t = time(NULL);\n");
    fprintf(out, "    struct tm tm = *localtime(&t);\n");
    fprintf(out, "    tape[11] = (unsigned char)((tm.tm_year + 1900) %% 100);\n");
    fprintf(out, "    tape[12] = (unsigned char)(tm.tm_mon + 1);\n");
    fprintf(out, "    tape[13] = (unsigned char)tm.tm_mday;\n");
    fprintf(out, "    tape[14] = (unsigned char)tm.tm_hour;\n");
    fprintf(out, "    tape[15] = (unsigned char)tm.tm_min;\n");
    fprintf(out, "    tape[16] = (unsigned char)tm.tm_sec;\n");
    fprintf(out, "    int offset = 17;\n");
    fprintf(out, "    for (int i = 0; i < argc; i++) {\n");
    fprintf(out, "        int len = strlen(argv[i]);\n");
    fprintf(out, "        if (offset + len + 1 >= 1024) break;\n");
    fprintf(out, "        strcpy((char*)(tape + offset), argv[i]);\n");
    fprintf(out, "        offset += len + 1;\n");
    fprintf(out, "    }\n\n");

    // RLE encoding parser
    int count = 0;
    char current_char = 0;
    
    for (int i = 0; bf_code[i] != '\0'; i++) {
        char c = bf_code[i];
        
        if (c == '>' || c == '<' || c == '+' || c == '-') {
            if (current_char == c) {
                count++;
            } else {
                // emit previous
                if (count > 0) {
                    if (current_char == '>') {
                        fprintf(out, "    ptr += %d; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;\n", count);
                    } else if (current_char == '<') {
                        fprintf(out, "    ptr -= %d; if (ptr < tape) ptr += TAPE_SIZE;\n", count);
                    } else if (current_char == '+') {
                        fprintf(out, "    (*ptr) += %d;\n", count);
                    } else if (current_char == '-') {
                        fprintf(out, "    (*ptr) -= %d;\n", count);
                    }
                }
                current_char = c;
                count = 1;
            }
        } else if (c == '.' || c == ',' || c == '[' || c == ']' || c == '#') {
            // emit pending RLE
            if (count > 0) {
                if (current_char == '>') {
                    fprintf(out, "    ptr += %d; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;\n", count);
                } else if (current_char == '<') {
                    fprintf(out, "    ptr -= %d; if (ptr < tape) ptr += TAPE_SIZE;\n", count);
                } else if (current_char == '+') {
                    fprintf(out, "    (*ptr) += %d;\n", count);
                } else if (current_char == '-') {
                    fprintf(out, "    (*ptr) -= %d;\n", count);
                }
                count = 0;
                current_char = 0;
            }
            // emit new
            if (c == '.') {
                fprintf(out, "    putchar(*ptr);\n");
            } else if (c == ',') {
                fprintf(out, "    *ptr = getchar();\n");
            } else if (c == '[') {
                fprintf(out, "    while (*ptr) {\n");
            } else if (c == ']') {
                fprintf(out, "    }\n");
            } else if (c == '#') {
                fprintf(out, "    handle_syscall(ptr);\n");
            }
        }
    }
    
    // flush pending
    if (count > 0) {
        if (current_char == '>') {
            fprintf(out, "    ptr += %d; if (ptr >= tape + TAPE_SIZE) ptr -= TAPE_SIZE;\n", count);
        } else if (current_char == '<') {
            fprintf(out, "    ptr -= %d; if (ptr < tape) ptr += TAPE_SIZE;\n", count);
        } else if (current_char == '+') {
            fprintf(out, "    (*ptr) += %d;\n", count);
        } else if (current_char == '-') {
            fprintf(out, "    (*ptr) -= %d;\n", count);
        }
    }
    
    fprintf(out, "    free(tape);\n");
    fprintf(out, "    return 0;\n");
    fprintf(out, "}\n");
}

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Usage: bfc <input.bf> [-o output_binary]\n");
        return 1;
    }
    
    const char* input_file = argv[1];
    const char* output_bin = "a.out";
    
    if (argc == 4 && strcmp(argv[2], "-o") == 0) {
        output_bin = argv[3];
    }
    
    FILE* f = fopen(input_file, "r");
    if (!f) {
        printf("Failed to open %s\n", input_file);
        return 1;
    }
    
    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    char* bf_code = malloc(fsize + 1);
    fread(bf_code, 1, fsize, f);
    bf_code[fsize] = 0;
    fclose(f);
    
    char c_file[1024];
    snprintf(c_file, sizeof(c_file), "%s.c", input_file);
    
    FILE* out = fopen(c_file, "w");
    if (!out) {
        printf("Failed to create %s\n", c_file);
        free(bf_code);
        return 1;
    }
    
    compile_bf_to_c(bf_code, out);
    fclose(out);
    free(bf_code);
    
    printf("Transpiled to %s, compiling with GCC -O3...\n", c_file);
    
    char cmd[2048];
    snprintf(cmd, sizeof(cmd), "gcc -O3 \"%s\" -o \"%s\"", c_file, output_bin);
    int res = system(cmd);
    
    if (res == 0) {
        printf("Successfully compiled native binary: %s\n", output_bin);
        return 0;
    } else {
        printf("GCC compilation failed.\n");
        return 1;
    }
}
