import sys

def evaluate(code):
    tape = [0] * 30000
    ptr = 0
    pc = 0
    
    # Precompute loop jumps
    loop_map = {}
    stack = []
    for i, c in enumerate(code):
        if c == '[':
            stack.append(i)
        elif c == ']':
            if not stack:
                raise Exception(f"Unmatched ] at {i}")
            start = stack.pop()
            loop_map[start] = i
            loop_map[i] = start
            
    if stack:
        raise Exception(f"Unmatched [ at {stack.pop()}")
        
    output = []
    
    while pc < len(code):
        c = code[pc]
        if c == '>':
            ptr += 1
            if ptr >= len(tape):
                tape.extend([0] * 30000)
        elif c == '<':
            ptr -= 1
            if ptr < 0:
                raise Exception("Pointer went below 0")
        elif c == '+':
            tape[ptr] = (tape[ptr] + 1) % 256
        elif c == '-':
            tape[ptr] = (tape[ptr] - 1) % 256
        elif c == '.':
            sys.stdout.write(chr(tape[ptr]))
            sys.stdout.flush()
        elif c == ',':
            char = sys.stdin.read(1)
            if char:
                tape[ptr] = ord(char)
        elif c == '[':
            if tape[ptr] == 0:
                pc = loop_map[pc]
        elif c == ']':
            if tape[ptr] != 0:
                pc = loop_map[pc]
        pc += 1

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        evaluate(f.read())
