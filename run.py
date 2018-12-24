#!/usr/bin/env python3

import sys

def load_program():
    with open("challenge.bin", "rb") as f:
        g = f.read()

    program = [0] * ((1<<15) + 8)
    for i in range(0, len(g), 2):
        u = g[i]
        v = g[i+1]

        program[i // 2] = (u + (v << 8))

    return program

def handle_input(fname=None):
    # This function generates input from command line, one char at a time
    if fname is not None:
        with open(fname, 'r') as f:
            for line in f:
                if line.startswith('"'):
                    continue
                print(line, end='')
                yield from process(line.strip())

    with open("record", 'w') as f:
        while True:
            u = input()
            f.write(u + "\n")
            yield from process(u)

def display(p):
    def display_helper(x):
        if x >> 15:
            return chr((x & 0b111) + ord('A'))
        return str(x)

    op_code = prog[p]
    if op_list[op_code].__name__ == "out":
        print("p = {:4d} out {}".format(p, chr(prog[p + 1])).strip())
    else:
        print("p = {:4d} {:5s}".format(p, op_list[op_code].__name__),
            " ".join(display_helper(prog[p + i]) for i in range(1, op_len[op_code])))

def stat():
    print("stack_len = {}, top of stack: {}".format(len(stack), stack[-6:]))
    print(prog[-8:])

def process(u):
    if u == "verbose":
        global verbose
        verbose = True
    elif u == "stat":
        stat()
    elif u.startswith("set"):
        prog[-1] = int(u.split()[-1])
    else:
        for char in u:
            yield char
        yield "\n"

prog = load_program()
handler = handle_input(sys.argv[1] if 1 < len(sys.argv) else None)
verbose = False

def reg(x):
    return (1 << 15) + x
# for i, x in enumerate([ 1, reg(0), 32758,
#          1, reg(1), 15,
#          9, reg(2), reg(0), reg(1),
#          19, reg(0),
#          19, reg(1),
#          19, reg(2),
#         0
#         ]):
#     prog[i] = x

stack = []
op_list = [None]*22
op_len = [None]*22

BITMASK_15 = (1<<15) - 1

def add_to_op_list(i, n):
    def decorate(f):
        op_list[i] = f
        op_len[i] = n
    return decorate

def read(x):
    if x >> 15:
        return prog[x]
    return x

def write(x, val):
    prog[x] = val

class ProgramExit(Exception):
    pass

@add_to_op_list(0, 1)
def halt(p):
    # print("Final registers: {}".format(prog[-8:]))
    # print("Final stack: {}".format(stack))
    raise ProgramExit

@add_to_op_list(1, 3)
def set(p):
    write(prog[p+1], read(prog[p+2]))
    return p + 3

@add_to_op_list(2, 2)
def push(p):
    stack.append(read(prog[p+1]))
    return p + 2

@add_to_op_list(3, 2)
def pop(p):
    write(prog[p+1], stack.pop())
    return p + 2

@add_to_op_list(6, 2)
def jmp(p):
    return read(prog[p+1])

@add_to_op_list(7, 3)
def jt(p):
    if read(prog[p+1]):
        return read(prog[p+2])
    return p + 3

@add_to_op_list(8, 3)
def jf(p):
    if not read(prog[p+1]):
        return read(prog[p+2])
    return p + 3

def two_arg_func(f):
    def func(p):
        val = f(read(prog[p+2]), read(prog[p+3]))
        write(prog[p+1], val)
        return p + 4
    func.__name__ = f.__name__
    return func

@add_to_op_list(4, 4)
@two_arg_func
def eq(x, y):
    return int(x == y)

@add_to_op_list(5, 4)
@two_arg_func
def gt(x, y):
    return int(x > y)

@add_to_op_list(9, 4)
@two_arg_func
def add(x, y):
    return (x + y) & BITMASK_15

@add_to_op_list(10, 4)
@two_arg_func
def mult(x, y):
    return (x * y) & BITMASK_15

@add_to_op_list(11, 4)
@two_arg_func
def mod(x, y):
    return x % y

@add_to_op_list(12, 4)
@two_arg_func
def _and(x, y):
    return x & y

@add_to_op_list(13, 4)
@two_arg_func
def _or(x, y):
    return x | y

@add_to_op_list(14, 3)
def _not(p):
    write(prog[p+1], BITMASK_15 ^ read(prog[p+2]))
    return p + 3

@add_to_op_list(15, 3)
def rmem(p):
    """
    rmem a b : read memory at address <b> and write it to <a>
    """
    address = read(prog[p + 2])
    val = prog[address]
    write(prog[p + 1], val)
    return p + 3

@add_to_op_list(16, 3)
def wmem(p):
    """
    wmem a b : write the value from <b> into memory at address <a>
    """
    val = read(prog[p + 2])
    address = read(prog[p + 1])
    prog[address] = val
    return p + 3

@add_to_op_list(17, 2)
def call(p):
    stack.append(p + 2)
    return read(prog[p + 1])

@add_to_op_list(18, 1)
def ret(p):
    try:
        val = stack.pop()
    except IndexError:
        raise ProgramExit
    return val

@add_to_op_list(19, 2)
def out(p):
    print(chr(read(prog[p + 1])), end='')
    return p + 2

@add_to_op_list(20, 2)
def _in(p):
    val = ord(next(handler))
    write(prog[p + 1], val)
    return p + 2

@add_to_op_list(21, 1)
def noop(p):
    return p + 1

def run():
    pointer = 0
    try:
        while True:
            # if pointer == 5472:
            #     global verbose
            #     verbose = True
            # if verbose:
            #     x = input()
            #     if pointer in [5489, 6027]:
            #         stat()
            #     print("Calling", end=' ')
            #     display(pointer)

            pointer = op_list[prog[pointer]](pointer)
    except ProgramExit:
        pass

def remove_safety():
    new_code_pointer = 32764
    # Call new function instead of old one
    prog[5490] = new_code_pointer

    for i, x in enumerate([1, reg(0), 6, 18]):
        prog[new_code_pointer + i] = x

if __name__=="__main__":
    remove_safety()
    run()
