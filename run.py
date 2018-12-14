#!/usr/bin/env python3

import sys

def load_program(filename):
    with open(filename, "rb") as f:
        g = iter(f.read())

    program = []
    while True:
        try:
            u = next(g)
            v = next(g)
        except StopIteration:
            return program

        program.append(u + (v << 8))

def handle_input():
    # This function generates input from command line, one char at a time
    while True:
        u = input()
        for char in u:
            yield char
        yield "\n"

handler = handle_input()

if len(sys.argv) < 2:
    print("Input file required")
    exit(1)
prog = load_program(sys.argv[1])

# def reg(x):
#     return (1 << 15) + x
# prog = [ 1, reg(0), 101,
#         20, reg(2),
#         19, reg(0),
#         19, reg(2),
#         0
#         ]

registers = [0]*8
stack = []
op_list = [None]*22

BITMASK_15 = (1<<15) - 1

def add_to_op_list(i):
    def decorate(f):
        def new_f(*args):
            # For debugging
            # print("Calling op: {}".format(f.__name__))
            return f(*args)
        op_list[i] = new_f
    return decorate

def read(x):
    if x >> 15:
        return registers[x & 0b111]
    return x

def write(x, val):
    registers[x & 0b111] = val

@add_to_op_list(0)
def halt(p):
    # print("Final registers: {}".format(registers))
    # print("Final stack: {}".format(stack))
    exit(0)

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
        exit(0)
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
    while True:
        # print("Calling {}".format(prog[pointer]))
        pointer = op_list[prog[pointer]](pointer)

run()
