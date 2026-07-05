import sys

def run(code, input_data=b''):
    tape = [0] * 30000
    ptr = 1024
    pc = 0
    out = []
    
    bracket_map = {}
    stack = []
    for i, c in enumerate(code):
        if c == '[': stack.append(i)
        elif c == ']':
            start = stack.pop()
            bracket_map[start] = i
            bracket_map[i] = start
            
    while pc < len(code):
        c = code[pc]
        if c == '>': ptr += 1
        elif c == '<': ptr -= 1
        elif c == '+': tape[ptr] = (tape[ptr] + 1) % 256
        elif c == '-': tape[ptr] = (tape[ptr] - 1) % 256
        elif c == '.': 
            out.append(chr(tape[ptr]))
            if chr(tape[ptr]) == 'X':
                print(f"DEBUG: printed X! ptr={ptr}, tape[ptr]={tape[ptr]}")
                print(f"Tape at 1024: {tape[1024:1034]}")
                break
        elif c == ',': pass
        elif c == '[':
            if tape[ptr] == 0: pc = bracket_map[pc]
        elif c == ']':
            if tape[ptr] != 0: pc = bracket_map[pc]
        pc += 1
    return "".join(out)

print(run(open('test_all.bf').read()))
