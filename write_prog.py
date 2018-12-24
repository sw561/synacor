#!/usr/bin/env python3

from run import *
from heapq import heapify, heappush, heappop

def list_code(h):
    p = heappop(h)
    while p < len(prog) or h:
        if p >= len(prog) or prog[p] >= len(op_len):
            c = 0
            while h and c < p:
                c = heappop(h)
            if c > p:
                p = c
                continue
            else:
                return

        op_code = prog[p]

        display(p)

        if (op_list[op_code].__name__.startswith("j") or op_list[op_code].__name__ == "call")\
                and not prog[p+op_len[op_code]-1] >> 15:
            heappush(h, prog[p + 1])

        p += op_len[op_code]

h = [0, 5478]
heapify(h)
remove_safety()
list_code(h)
