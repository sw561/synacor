#!/usr/bin/env python3

import sys

def load_program(filename):
    with open(filename, "rb") as f:
        g = f.read()

    program = [None] * ((1<<15) + 8)
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
                print(line, end='')
                yield from line

    with open("record", 'w') as f:
        while True:
            u = input()
            f.write(u + "\n")
            for char in u:
                yield char
            yield "\n"

if len(sys.argv) < 2:
    print("Input file required")
    exit(1)
prog = load_program(sys.argv[1])
handler = handle_input(sys.argv[2] if 2 < len(sys.argv) else None)

# def reg(x):
#     return (1 << 15) + x
# prog = [ 1, reg(0), 101,
#         20, reg(2),
#         19, reg(0),
#         19, reg(2),
#         0
#         ]

stack = []
op_list = [None]*22

BITMASK_15 = (1<<15) - 1

def add_to_op_list(i):
    def decorate(f):
        # def new_f(*args):
        #     # For debugging
        #     print("Calling op: {}".format(f.__name__))
        #     return f(*args)
        op_list[i] = f
    return decorate

def read(x):
    if x >> 15:
        return prog[x]
    return x

def write(x, val):
    prog[x] = val

class ProgramExit(Exception):
    pass

@add_to_op_list(0)
def halt(p):
    # print("Final registers: {}".format(prog[-8:]))
    # print("Final stack: {}".format(stack))
    raise ProgramExit

@add_to_op_list(1)
def set(p):
    write(prog[p+1], read(prog[p+2]))
    return p + 3

@add_to_op_list(2)
def push(p):
    stack.append(read(prog[p+1]))
    return p + 2

@add_to_op_list(3)
def pop(p):
    write(prog[p+1], stack.pop())
    return p + 2

@add_to_op_list(6)
def jmp(p):
    return read(prog[p+1])

@add_to_op_list(7)
def jt(p):
    if read(prog[p+1]):
        return read(prog[p+2])
    return p + 3

@add_to_op_list(8)
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

@add_to_op_list(4)
@two_arg_func
def eq(x, y):
    return int(x == y)

@add_to_op_list(5)
@two_arg_func
def gt(x, y):
    return int(x > y)

@add_to_op_list(9)
@two_arg_func
def add(x, y):
    return (x + y) & BITMASK_15

@add_to_op_list(10)
@two_arg_func
def mult(x, y):
    return (x * y) & BITMASK_15

@add_to_op_list(11)
@two_arg_func
def mod(x, y):
    return x % y

@add_to_op_list(12)
@two_arg_func
def _and(x, y):
    return x & y

@add_to_op_list(13)
@two_arg_func
def _or(x, y):
    return x | y

@add_to_op_list(14)
def _not(p):
    write(prog[p+1], BITMASK_15 ^ read(prog[p+2]))
    return p + 3

@add_to_op_list(15)
def rmem(p):
    """
    rmem a b : read memory at address <b> and write it to <a>
    """
    address = read(prog[p + 2])
    val = prog[address]
    write(prog[p + 1], val)
    return p + 3

@add_to_op_list(16)
def wmem(p):
    """
    wmem a b : write the value from <b> into memory at address <a>
    """
    val = read(prog[p + 2])
    address = read(prog[p + 1])
    prog[address] = val
    return p + 3

@add_to_op_list(17)
def call(p):
    stack.append(p + 2)
    return read(prog[p + 1])

@add_to_op_list(18)
def ret(p):
    try:
        val = stack.pop()
    except IndexError:
        raise ProgramExit
    return val

@add_to_op_list(19)
def out(p):
    print(chr(read(prog[p + 1])), end='')
    return p + 2

@add_to_op_list(20)
def _in(p):
    val = ord(next(handler))
    write(prog[p + 1], val)
    return p + 2

@add_to_op_list(21)
def noop(p):
    return p + 1

def run():
    pointer = 0
    try:
        while True:
            # print("Calling {}".format(prog[pointer]))
            pointer = op_list[prog[pointer]](pointer)
    except ProgramExit:
        pass

run()
