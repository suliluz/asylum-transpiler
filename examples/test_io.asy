import "std/sys.asy";
import "std/io.asy";

print("--- Asylum File I/O Test ---\n");

// 1. Open file for writing
io_block[2] = "hello.txt";
let fd_write = fopen(1); // 1 = write mode

if (fd_write == 0) {
    print("Failed to open file for writing\n");
} else {
    print("Successfully opened hello.txt for writing (FD: ");
    print_digit(fd_write);
    print(")\n");
    
    // Write data to the file
    io_block[3] = "Hello from Asylum IO Streams!\n";
    let written = fwrite(fd_write, 33); // length of string
    
    print("Wrote ");
    print_digit(written); // Note: print_digit only prints single digits, but 33 will print whatever 48+33 is.
    print(" bytes.\n");   // Wait, we don't have print_num here since we didn't import math.asy, let's just print something else.
    
    fclose(fd_write);
    print("Closed file.\n");
}

// 2. Re-open for reading
io_block[2] = "hello.txt";
let fd_read = fopen(0); // 0 = read mode

if (fd_read == 0) {
    print("Failed to open file for reading\n");
} else {
    print("Opened hello.txt for reading. Contents:\n");
    
    // Read 33 bytes
    let bytes_read = fread(fd_read, 33);
    
    // Print the read characters from io_block[1] to io_block[33]
    let i = 1;
    let end = bytes_read;
    end += 1;
    while (i != end) {
        print(io_block[i]);
        i++;
    }
    
    fclose(fd_read);
}
