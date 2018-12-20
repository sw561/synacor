#!/usr/bin/env python3

from itertools import permutations

coins = {2: "red", 9: "blue", 5: "shiny", 3: "corroded", 7: "concave"}

for p in permutations(coins.keys()):
    x = p[0] + p[1] * p[2]**2 + p[3]**3 - p[4]
    if x == 399:
        print(" ".join(coins[pi] for pi in p))
        break
