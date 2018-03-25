from functools import partial, reduce
import operator
import random

def zipfunc(*args, func=None):
    return tuple(reduce(func, elems) for elems in zip(*args))

#zipsum = partial(zipfunc, func=operator.add)
zipsub = partial(zipfunc, func=operator.sub)
zipmul = partial(zipfunc, func=operator.mul)

def zipsum(first, second):
    return tuple(a + b for a, b in zip(first, second))

def random_pop(lst):
    idx = random.randint(0, len(lst) - 1)
    return lst.pop(idx)
