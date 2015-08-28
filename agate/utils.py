#!/usr/bin/env python

from functools import wraps

def memoize(func):
    """
    Dead-simple memoize decorator for instance methods that take no arguments.

    This is especially useful since so many of our classes are immutable.
    """
    memo = None

    @wraps(func)
    def wrapper(self):
        if memo is not None:
            return memo

        return func(self)

    return wrapper

class NullOrder(object):
    """
    Dummy object used for sorting in place of None.

    Sorts as "greater than everything but other nulls."
    """
    def __lt__(self, other):
        return False

    def __gt__(self, other):
        if other is None:
            return False

        return True
