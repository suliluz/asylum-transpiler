# Asylum

**Asylum** is an experimental, AOT-compiled systems programming language that compiles directly down to Brainfuck, which is then transpiled by a native tool into highly optimized x86_64 machine code via C.

---

## 🧠 Architecture Pipeline

Unlike standard high-level languages, Asylum embraces the absolute absurdity of building complex applications on a 1MB linear memory tape. The compilation pipeline (`asyc`) works in two completely distinct phases:

1. **Frontend (`.asy` -> `.bf`)**: Written in Python, the frontend parser resolves imports, calculates static memory addresses, unwinds function calls into raw data manipulation, and generates standard Brainfuck instructions.
2. **Backend (`.bf` -> `.bin`)**: Written entirely in C (`src/bfc.c`), the native Brainfuck compiler ingests the `.bf` code, performs aggressive Run-Length Encoding (RLE) to group instructions, and uses GCC to build a memory-safe, standalone native binary. 

*Because of the native `.bf` compiler, Asylum's intermediate Brainfuck code is a first-class compilation artifact. You can compile any `.bf` file directly to a native Linux binary without the original `.asy` source!*

---

## ✨ Features

- **Turing Tarpit Mastery**: Full AOT compilation into an instruction set containing only 8 symbols (`> < + - . , [ ]`), plus one custom hardware interrupt (`#`).
- **Memory-Safe 1MB Tape**: The runtime allocates a strict 1MB tape. Static variables grow upwards from `1024`, while dynamic memory (`malloc`) grows downwards from the end of the tape (`1048576`). 
- **Hardware Integrations**: OS Command Line Arguments (`argc`/`argv`) and System Date/Time are directly injected into the lower bounds of the tape *before* execution starts.
- **True Pointers & Dynamic Memory**: Using `#` interrupts, Asylum implements true 32-bit indirect memory access (`read_ptr`/`write_ptr`), allowing for runtime dynamic arrays and `malloc()`!
- **Networking & Graphics**: Native `#` interrupts allow the tape to interface directly with the Linux Kernel for file streams, TCP sockets (web servers!), and ANSI RGB framebuffer rendering!
- **No Python Runtime**: Applications built with `asyc build` are entirely standalone, self-contained native Linux binaries.

---

## 🛠️ Writing Apps in Asylum

### Memory Layout
There is **no dynamic heap allocator** in Asylum. Every variable, array, and structure must be mapped to a specific offset on the 1MB tape.

By convention, the first `1024` bytes (Addresses `0-1023`) are reserved for the OS environment (CLI arguments, date/time, and the Syscall I/O blocks). 

**Your application should always start allocating variables at address `1024` or higher.**

### Variables & Data Types
All data in Asylum is ultimately an **8-bit unsigned integer** (Byte), wrapping from `0` to `255`. 

You can explicitly map variables using `@ [address]`, or you can simply let the compiler automatically assign the next available tape address for you (starting from `1024`)!

```typescript
// Explicitly map a variable to address 1024
let explicit_var @ 1024 = 42;

// Or let the compiler automatically assign the next available address
let auto_var = 100;

// Arrays reserve sequential memory
let message : byte[5]; // Automatically allocated 5 sequential bytes
message[0] = 72; // 'H'
message[1] = 105; // 'i'
```

### The Standard Library
To save you from the madness of raw tape manipulation, Asylum comes with a robust standard library:

#### 1. System/Time (`std/sys.asy`)
Accesses OS-injected variables automatically.
```typescript
import "std/sys.asy";

// Get the current system time (injected by the runtime)
let year = sys_year;
let month = sys_month;
```

#### 2. Mathematics (`std/math.asy`)
Provides standard arithmetic. Because the CPU only knows `+` and `-`, all math is executed via highly-optimized looping constructs.
```typescript
import "std/math.asy";

let result = mul(6, 7); // 42
let remainder = mod(10, 3); // 1
```

#### 3. File I/O (`std/io.asy`)
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
```

#### 4. Networking (`std/net.asy`)
TCP sockets and Web Servers straight from the Brainfuck VM.
```typescript
import "std/net.asy";

let server = net_socket();
// Ports are 16-bit integers, split into high and low bytes.
// 8080 = (31 * 256) + 144
net_bind_listen(server, 31, 144); 
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

// Since functions can only return a single byte, malloc populates
// the newly allocated 32-bit pointer into bytes 5-8 of _ptr_block.
let p0 = _ptr_block[5];
let p1 = _ptr_block[6];
let p2 = _ptr_block[7];
let p3 = _ptr_block[8];

print_str_ptr(p0, p1, p2, p3);
```

---

## 🚀 CLI Usage

The `asyc` tool handles the entire pipeline for you.

```bash
# Compile and run a script in memory
./asyc run examples/test_math.asy

# Compile a script into a native standalone binary
./asyc build examples/test_io.asy -o io_app

# Emit the intermediate Brainfuck code
./asyc emit-bf examples/test_date.asy

# Emit the heavily-optimized C transpilation
./asyc emit-c examples/test_date.asy
```

*(Note: The internal `src/bfc` binary must be compiled first for the toolchain to function. Run `gcc -O3 src/bfc.c -o src/bfc` if the backend is missing).*

---

## ⚠️ Disclaimers

> [!WARNING]
> This project was generated entirely by an AI (Google DeepMind's Gemini) out of boredom as a hobby/experimental project. 

**This is absolutely not suitable for production use.** 

The entire language is built on top of a Turing Tarpit and uses aggressive memory manipulation, unsafe bounds wrapping, and completely non-standard intermediate representations to achieve I/O streams and math operations. 

There is no semantic analysis pass, no type checking, and all integers are strictly 8-bit unsigned bytes (0-255). Expect aggressive overflow wrapping, 32-bit pointers split manually across 4 individual bytes, and highly volatile memory states if you deviate from the standard library.

Use at your own risk!