
count = 0

def cache(f):
    d = dict()
    def cached_f(*args):
        if args not in d:
            d[args] = f(*args)
        return d[args]
    return cached_f

# @cache
def f(a, b):
    global count
    if count == 40:
        exit()
    else:
        count += 1
    print("Calling f, a = {} b = {}".format(a, b))
    if a==0:
        return b + 1
    if b==0:
        return f(a-1, h)
    return f(a-1, f(a, b-1))

h = 1
a = 4
b = 1
f(a, b)

# Find h s.t. f(4, 1) == 6
