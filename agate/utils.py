#!/usr/bin/env python

"""
This module contains common utilities used in agate.
"""

from collections import Sequence
from functools import wraps
import math

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

class Quantiles(Sequence):
    """
    A class representing quantiles (percentiles, quartiles, etc.) for a given
    column of Number data.
    """
    def __init__(self, quantiles):
        self._quantiles = quantiles

    def __getitem__(self, i):
        return self._quantiles.__getitem__(i)

    def __iter__(self):
        return self._quantiles.__iter__()

    def __len__(self):
        return self._quantiles.__len__()

    def __repr__(self):
        return repr(self._quantiles)

    def locate(self, value):
        """
        Identify which quantile a given value is part of.
        """
        i = 0

        if value < self._quantiles[0]:
            raise ValueError('Value is less than minimum quantile value.')

        if value > self._quantiles[-1]:
            raise ValueError('Value is greater than maximum quantile value.')

        if value == self._quantiles[-1]:
            return len(self._quantiles) - 1

        while value >= self._quantiles[i + 1]:
            i += 1

        return i
