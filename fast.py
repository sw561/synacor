#!/usr/bin/env python3

# f(0, b) = b + 1
#
# f(1, 0) = f(0, h) = h + 1
# f(1, b) = f(0, f(1, b-1))
#         = f(1, b-1) + 1
#         = h + 1 + b
#
# f(2, 0) = f(1, h)
#         = 2h + 1
# f(2, b) = f(1, f(2, b-1))
#         = h + 1 + f(2, b-1)
#         = 2h + 1 + (h+1)*b

def solve(h, u):
    # using definition for f in translation.py
    # evaluate f(4, 1) for given h

    # Calculate values for a=3 directly, and store in u s.t.
    # f(3, b) = u[b]
    #
    # Use
    # f(3, 0) = f(2, h)
    # f(3, b) = f(2, f(3, b-1))

    u[0] = (h*(h + 3) + 1) & 0x7fff
    for b in range(1, h+1):
        u[b] = ((2+u[b-1])*h + 1 + u[b-1]) & 0x7fff

    # print(u[:20])

    # f(4, 0) = f(3, h)
    # f(4, 1) = f(3, f(4, 0))
    f40 = u[h]

    for b in range(h+1, f40+1):
        u[b] = ((2+u[b-1])*h + 1 + u[b-1]) & 0x7fff

    return u[f40]

u = [None]*(1 << 15)

def find_h():
    for h in range(1 << 15):
        # print("h = {}".format(h))
        x = solve(h, u)
        # print("----")

        if x == 6:
            return h

        if not h & 0b111111:
            print(h)

def check(h):
    assert solve(h, u) == 6

h = find_h()
print(h)

# h = 25734
# check(h)
