import sys

def execute(code):
    tape = [0] * 30000
    ptr = 1024
    pc = 0
    bracket_map = {}
    stack = []
    
    for i, c in enumerate(code):
        if c == '[': stack.append(i)
        elif c == ']':
            start = stack.pop()
            bracket_map[start] = i
            bracket_map[i] = start
            
    out = ""
    while pc < len(code):
        c = code[pc]
        if c == '>': ptr += 1
        elif c == '<': ptr -= 1
        elif c == '+': tape[ptr] = (tape[ptr] + 1) % 256
        elif c == '-': tape[ptr] = (tape[ptr] - 1) % 256
        elif c == '.': out += chr(tape[ptr])
        elif c == '[':
            if tape[ptr] == 0: pc = bracket_map[pc]
        elif c == ']':
            if tape[ptr] != 0: pc = bracket_map[pc]
        pc += 1
    print("OUTPUT:", out)
    print("ERR_FLAG (addr 1 -> 1025):", tape[1025])

execute(open(sys.argv[1]).read())
