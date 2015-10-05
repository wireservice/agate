#!/usr/bin/env python

"""
This module contains a collection of utility classes and functions used in
agate.
"""

from collections import Sequence
from functools import wraps

class Patchable(object):
    """
    Adds a monkeypatching extensibility pattern to subclasses.

    Calling :code:`Class.monkeypatch(AnotherClass)` will dynamically add
    :code:`AnotherClass` as a base class of :code:`Class`. This effective is
    global--even existing instances of the class will have the new methods.

    This can only be used to add new methods. It can not be used to override
    the implementation of an existing method on the patched class.
    """
    @classmethod
    def monkeypatch(cls, patch_cls):
        """
        Dynamically add :code:`patch_cls` as a base class of this class.

        :param patch_cls: The class to be patched on.
        """
        if patch_cls in cls.__bases__:
            return

        cls.__bases__ += (patch_cls, )

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

def median(data_sorted):
    """
    Finds the median value of a given series of values.

    :param data_sorted: The values to find the median of. Must be sorted.
    """
    length = len(data_sorted)

    if length % 2 == 1:
        return data_sorted[((length + 1) // 2) - 1]

    half = length // 2
    a = data_sorted[half - 1]
    b = data_sorted[half]

    return (a + b) / 2

def max_precision(values):
    """
    Given a series of values (such as a :class:`.Column`) returns the most
    significant decimal places present in any value.

    :param values: The values to analyze.
    """
    max_places = 0

    for i, value in enumerate(values):
        if value is None:
            continue

        places = value.normalize().as_tuple().exponent * -1

        if places > max_places:
            max_places = places

    return max_places
