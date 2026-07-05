import sys

def execute(code):
    tape = [0] * 30000
    ptr = 0
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

# err_flag=1, err_copy=2, not_err=3, temp=4
bf = """
> + <    // set err_flag to 1
>>> [-]+ <<<  // set not_err to 1

// copy err_flag to err_copy
>[-]<
>>>>[-]<<<<
>[->+>>+<<<]>[-<+>]<

// not_err check
>> [- <<< [-] >>> ] <<

// if not_err (should be skipped!)
> [
    +++++ +++++ . // print newline (char 10)
    [-]
]
"""
execute(bf)
