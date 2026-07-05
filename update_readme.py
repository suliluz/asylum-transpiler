with open("README.md", "r") as f:
    text = f.read()

# Update Features
old_features = """## ✨ Features

- **Turing Tarpit Mastery**: Full AOT compilation into an instruction set containing only 8 symbols (`> < + - . , [ ]`), plus one custom hardware interrupt (`#`).
- **Memory-Safe 1MB Heap**: The runtime allocates a strict 1MB tape. Aggressive memory boundaries are enforced natively in the compiler; moving the pointer out-of-bounds will seamlessly wrap around without segfaulting.
- **Hardware Integrations**: OS Command Line Arguments (`argc`/`argv`) and System Date/Time are directly injected into the lower bounds of the tape *before* execution starts.
- **File I/O Streams**: A native `#` syscall interrupt allows the Brainfuck tape to interface directly with the Linux Kernel for file streams (`fopen`, `fread`, `fwrite`, `fclose`).
- **No Python Runtime**: Applications built with `asyc build` are entirely standalone, self-contained native Linux binaries."""

new_features = """## ✨ Features

- **Turing Tarpit Mastery**: Full AOT compilation into an instruction set containing only 8 symbols (`> < + - . , [ ]`), plus one custom hardware interrupt (`#`).
- **Memory-Safe 1MB Tape**: The runtime allocates a strict 1MB tape. Static variables grow upwards from `1024`, while dynamic memory (`malloc`) grows downwards from the end of the tape (`1048576`). 
- **Hardware Integrations**: OS Command Line Arguments (`argc`/`argv`) and System Date/Time are directly injected into the lower bounds of the tape *before* execution starts.
- **True Pointers & Dynamic Memory**: Using `#` interrupts, Asylum implements true 32-bit indirect memory access (`read_ptr`/`write_ptr`), allowing for runtime dynamic arrays and `malloc()`!
- **Networking & Graphics**: Native `#` interrupts allow the tape to interface directly with the Linux Kernel for file streams, TCP sockets (web servers!), and ANSI RGB framebuffer rendering!
- **No Python Runtime**: Applications built with `asyc build` are entirely standalone, self-contained native Linux binaries."""
text = text.replace(old_features, new_features)

# Update Disclaimers
old_disc = """There is no semantic analysis pass, no type checking, no dynamic heap allocation, and all integers are strictly 8-bit unsigned bytes (0-255). Expect aggressive overflow wrapping, lack of true pointers, and highly volatile memory states if you deviate from the standard library or misalign your fixed memory addresses."""
new_disc = """There is no semantic analysis pass, no type checking, and all integers are strictly 8-bit unsigned bytes (0-255). Expect aggressive overflow wrapping, 32-bit pointers split manually across 4 individual bytes, and highly volatile memory states if you deviate from the standard library."""
text = text.replace(old_disc, new_disc)

# Add Standard Library sections for Net, Ptr, Gfx
lib_end = """#### 3. File I/O (`std/io.asy`)
Wraps the `#` hardware interrupt to provide access to File Streams.
```typescript
import "std/io.asy";

// Open file
io_block[2] = "hello.txt";
let fd = fopen(1); // 1 = Write mode

// Write to file
io_block[3] = "Hello World!";
fwrite(fd, 12);

// Close
fclose(fd);
```"""

new_libs = lib_end + """

#### 4. Networking (`std/net.asy`)
TCP sockets and Web Servers straight from the Brainfuck VM.
```typescript
import "std/net.asy";

let server = net_socket();
net_bind_listen(server, 31, 144); // 8080
let client = net_accept(server);

// ... manual string population ...
net_send(client, 0, 22);
net_close(client);
```

#### 5. Dynamic Memory & Pointers (`std/mem.asy`, `std/ptr.asy`)
```typescript
import "std/mem.asy";
import "std/string.asy";

// Allocate 20 bytes dynamically from the end of the tape
malloc(0, 0, 0, 20);

// Use the returned 32-bit pointer natively
let p0 = _ptr_block[5];
let p1 = _ptr_block[6];
let p2 = _ptr_block[7];
let p3 = _ptr_block[8];

print_str_ptr(p0, p1, p2, p3);
```"""

text = text.replace(lib_end, new_libs)

with open("README.md", "w") as f:
    f.write(text)
