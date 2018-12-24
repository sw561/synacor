#!/usr/bin/env python3

def make_mask(n):
    return (1 << n) - 1

def f2(h, b, mask=make_mask(15)):
    return (2*h + 1 + (h+1)*b) & mask

def solve(h, u):
    # evaluate f(4, 1) for given h

    # f(0, b) = b + 1
    #
    # f(1, 0) = f(0, h) = h + 1
    # f(1, b) = f(0, f(1, b-1))
    #         = f(1, b-1) + 1
    #         = h + 1 + b
    #
    # f(2, 0) = f(1, h)
    #         = 2h + 1
    # f(2, i) = f(1, f(2, b-1))
    #         = h + 1 + f(2, b-1)
    #         = 2h + 1 + (h+1)*b

    # Calculate values for a=3 directly
    # f(3, b) = u[b]
    u[0] = f2(h, h)
    for b in range(1, len(u)):
        u[b] = f2(h, u[b-1])

    # print(u[:20])

    # f(4, 1) = f(3, f(4, 0))
    # f(4, 0) = f(3, h)
    f40 = u[h]
    return u[f40]

u = [None]*(1 << 15)

def find_h():
    for h in range(1, 1 << 15):
        # print("h = {}".format(h))
        x = solve(h, u)
        # print("----")
        if x == 6:
            print(h)
            return
        if not h & 0b111111:
            print(h)

def check(h):
    print(h)
    solve(h, u)
    x = u[h]
    print(u[x])

check(25734)
