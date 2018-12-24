#!/usr/bin/env python3

from collections import deque

m = [
['*',  '8',  '-',  '1'],
['4',  '*', '11',  '*'],
['+',  '4',  '-', '18'],
['22',  '-',  '9',  '*'],
]

def unfiltered_neighbours(i, j):
    yield 'N', i-1, j
    yield 'S', i+1, j
    yield 'W', i, j-1
    yield 'E', i, j+1

def neighbours(i, j):
    for direction, x, y in unfiltered_neighbours(i, j):
        if 0 <= x < 4 and 0 <= y < 4:
            yield direction, x, y

# Use BFS to find route such that we reach value of 30 at the end

def find_routes():

    # Store tuples of position, weight
    d = deque([("", (3, 0), 22, None)])

    while d:

        path, (i, j), weight, op = d.popleft()

        for direction, x, y in neighbours(i, j):
            if op is None:
                new_op = m[x][y]
                new_weight = weight
            else:
                new_op = None
                new_weight = eval("{} {} {}".format(weight, op, m[x][y]))

            new_path = path + direction

            if new_weight < 0:
                continue

            if x == 3 and y == 0:
                continue

            if x == 0 and y == 3:
                if new_weight == 30:
                    return new_path
                else:
                    continue

            d.append((new_path, (x, y), new_weight, new_op))

x = find_routes()
direction_names = {x[0].upper(): x for x in ["north", "south", "east", "west"]}

print("\n".join(direction_names[d] for d in x))
