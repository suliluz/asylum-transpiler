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
- **First-Class Callbacks**: Dynamically pass and invoke functions by resolving them to numerical IDs, enabling dynamic dispatch and functional programming paradigms without dynamic jumps.
- **High-Resolution Timer**: Access precise millisecond-level UNIX timestamps during runtime for benchmarking and game loops via `sys_millis()`.
- **No Python Runtime**: Applications built with `asyc build` are entirely standalone, self-contained native Linux binaries.

---

## 🛠️ Writing Apps in Asylum

### Memory Layout
There is **no dynamic heap allocator** in Asylum. Every variable, array, and structure must be mapped to a specific offset on the 1MB tape.

By convention, the first `1024` bytes (Addresses `0-1023`) are reserved for the OS environment (CLI arguments, date/time, and the Syscall I/O blocks). 

**Your application should always start allocating variables at address `1024` or higher.**

### Variables & Data Types
Asylum supports several primitive data types in its syntax to define memory shapes:
- **`byte` / `bool`**: The fundamental 8-bit unsigned integer (`0-255`). Booleans are syntactic sugar for `0` (false) and `1` (true).
- **`int`, `long`, `float`, `double`**: Multi-byte primitives parsed by the syntax (Note: At the lowest Brainfuck level, all math compiles down to 8-bit loop manipulation, but these types reserve wider contiguous cells on the tape).
- **`string`**: Null-terminated character sequences.
- **`type[N]` (Arrays)**: Static homogeneous sequences (e.g. `byte[5]`).

Because Brainfuck only operates on single cells, the core building block of all data is ultimately an **8-bit unsigned integer**, wrapping from `0` to `255`. 

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

#### 1. System/Time (`std/sys.asy` & `std/time.asy`)
Accesses OS-injected variables automatically and provides high-resolution timers.

**Available Injected Variables (`std/sys.asy`):**
- `argc`: Number of command-line arguments.
- `sys_year`: Current year (e.g., 26 for 2026).
- `sys_month`: Current month (1-12).
- `sys_day`: Day of the month (1-31).
- `sys_hour`, `sys_minute`, `sys_second`: Current local time.

```typescript
import "std/sys.asy";
import "std/time.asy";

// Get the system date (injected by the runtime)
let year = sys_year;
let month = sys_month;

// Get a high-resolution millisecond timer for benchmarking
sys_millis();
let current_ms = _sys_time_block[3]; // Grabs the lower 8-bits of the 32-bit timestamp
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

### First-Class Callbacks
You can pass functions around as variables! The transpiler dynamically maps every function to a unique numerical ID, and builds an intelligent dispatch table whenever a callback is invoked.

```typescript
func add(a: byte, b: byte) byte { return a + b; }
func sub(a: byte, b: byte) byte { return a - b; }

// Generic executor
func run_math(op_func: byte, x: byte, y: byte) byte {
    return op_func(x, y); 
}

let cb1 = add;
let cb2 = sub;

let result = run_math(cb1, 5, 3); // 8
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
---

## 📖 Developer Journal

### Tape Alignment & Pointer Desync ("Wrong Pointing")
One of the most persistent and time-consuming bugs throughout early development was keeping the Brainfuck memory head perfectly synchronized with the compiler's internal state. Because the compiler emits raw `>` and `<` instructions to navigate the 1MB tape, any off-by-one error in tracking `self.current_addr` would lead to catastrophic cascading failures. If a `while` loop exited with the pointer shifted even one cell over, all subsequent variables would be written to the wrong memory addresses (a phenomenon I called "wrong pointing"). Debugging this required dumping raw tape states and meticulously tracking movement offsets instruction-by-instruction until I built a robust `move_to(addr)` abstraction that guaranteed state consistency across AST node boundaries.

### Scope Memory Leaks and Tape Collisions
Early in development, I ran into insidious memory corruption bugs where nested function calls would silently overwrite active variables. The issue traced back to how the Memory Manager tracked the `next_free` pointer when pushing and popping scopes. When a scope was popped, the compiler was incorrectly restoring the allocator's high-water mark, leading to overlapping variable allocations on the tape. I fixed this by deeply refactoring the scope tree to correctly maintain isolated memory bounds and properly garbage collect temporary registers across scope boundaries.

### Literal Array Access Optimization
Accessing array elements dynamically (`arr[i]`) in Brainfuck inherently requires expensive tape loops to traverse memory by an arbitrary offset. However, I realized the transpiler was naively generating these massive, expensive dynamic lookup loops even for static literal accesses like `arr[3]`. I introduced an optimization pass in the generator so that if the index expression is a raw number literal, the transpiler skips the looping logic entirely and statically calculates the exact memory offset at compile-time, saving thousands of cycles.

### Hash Map Integrity & Collision Chaining
Building a standard library Hash Map (`std/map.asy`) directly in Brainfuck using a `djb2` string hashing algorithm was a monumental task. The biggest challenge was ensuring data integrity under heavy loads; early iterations would blindly overwrite keys if two strings resulted in the same hash bucket. I had to architect a robust, tape-native collision chaining mechanism that dynamically allocates linked-list nodes for bucket collisions, ensuring that large-scale dictionary operations remain perfectly intact on a 1MB linear tape.


### The $O(N)$ Tape Movement Bloat
One of the most challenging optimization hurdles I faced during development was an architectural flaw in how the transpiler handled exceptions (`try/catch` and error bubbling). In the initial design, the error flag (`__err_flag`) was statically hardcoded to memory address `0x01` on the tape. 

Because active memory scopes generally reside upwards of address `1024`, the Brainfuck generator was forcefully copying and checking the value of `0x01` before executing *every single statement* within a block to ensure an error hadn't been thrown. This meant the Brainfuck memory head was endlessly traversing 1000+ addresses left and right thousands of times per function! 

For heavily nested logic (like standard library hash maps), this caused the transpiled Brainfuck file size to explode to **5.3MB** and slowed GCC native compilation to a crawl.

**The Fix**: I overhauled the memory management system to use dynamic, block-local `$O(1)$` error bubbling. Instead of checking a global register, functions now allocate their own temporary error flags alongside their local variables. When a function completes, it propagates its local error state directly back up to its caller's local scope with minimal tape movement. 

This optimization successfully dropped the transpiled output size of my heaviest stress test by **80%** (down to 1.1MB), achieving near-instant execution times and exponentially faster GCC compilations.

### The Chained AST Operator Bug
Another tricky bug involved PEMDAS and chained math evaluations. The compiler initially struggled with expressions like `a + b * c ^ 3 - a / c`. Because the Lark parser flattened chained AST operators (like `add_expr`) into a single list of children, the backend evaluator—which naively expected only 3 children per node—was silently ignoring trailing operations (completely dropping the `- a / c` division). 

Furthermore, earlier implementations of `pow` and `mul` incorrectly copied source values into their destination registers instead of accumulating them (erasing the running product on every loop iteration). 

**The Fix**: I rewrote the evaluator loop to sequentially fold over all chained AST children left-to-right. I also corrected the Brainfuck tape manipulation inside the multiplication and exponentiation loops to properly accumulate mathematical results using temporary registers, finally stabilizing complex algebraic equations natively in Brainfuck.
