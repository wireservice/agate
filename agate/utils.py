#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains a collection of utility classes and functions used in
agate.
"""

from collections import OrderedDict, Sequence
from functools import wraps
import string

try:
    from cdecimal import Decimal, ROUND_FLOOR, ROUND_CEILING, getcontext
except ImportError:  # pragma: no cover
    from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, getcontext

from babel.core import default_locale
import six


#: Character to render for horizontal lines
HORIZONTAL_LINE = u'-'

#: Character to render for vertical lines
VERTICAL_LINE = u'|'

#: Character to render for bar chart units
BAR_MARK = u'░'

#: Printable character to render for bar chart units
PRINTABLE_BAR_MARK = u':'

#: Character to render for zero line units
ZERO_MARK = u'▓'

#: Printable character to render for zero line units
PRINTABLE_ZERO_MARK = u'|'

#: Character to render for axis ticks
TICK_MARK = u'+'

#: Characters to render for ellipsis
ELLIPSIS = u'...'

#: Default locale for number formatting
LC_NUMERIC = default_locale('LC_NUMERIC') or 'en_US'

#: Sentinal for use when `None` is an valid argument value
default = object()


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


def allow_tableset_proxy(func):
    """
    Decorator to flag that a given :class:`.Table` method can be proxied as a
    :class:`.TableSet` method.
    """
    func.allow_tableset_proxy = True

    return func


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

        :param patch_cls:
            The class to be patched on.
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
            return Decimal(len(self._quantiles) - 1)

        while value >= self._quantiles[i + 1]:
            i += 1

        return Decimal(i)


def median(data_sorted):
    """
    Finds the median value of a given series of values.

    :param data_sorted:
        The values to find the median of. Must be sorted.
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

    :param values:
        The values to analyze.
    """
    max_whole_places = 1
    max_decimal_places = 0
    precision = getcontext().prec

    for value in values:
        if value is None:
            continue

        sign, digits, exponent = value.normalize().as_tuple()

        exponent_places = exponent * -1
        whole_places = len(digits) - exponent_places

        if whole_places > max_whole_places:
            max_whole_places = whole_places

        if exponent_places > max_decimal_places:
            max_decimal_places = exponent_places

    # In Python 2 it was possible for the total digits to exceed the
    # available context precision. This ensures that can't happen. See #412
    if max_whole_places + max_decimal_places > precision:  # pragma: no cover
        max_decimal_places = precision - max_whole_places

    return max_decimal_places


def make_number_formatter(decimal_places):
    """
    Given a number of decimal places creates a formatting string that will
    display numbers with that precision.
    """
    fraction = '0' * decimal_places

    return ''.join(['#,##0.', fraction, ';-#,##0.', fraction])


def round_limits(minimum, maximum):
    """
    Rounds a pair of minimum and maximum values to form reasonable "round"
    values suitable for use as axis minimum and maximum values.

    Values are rounded "out": up for maximum and down for minimum, and "off":
    to one higher than the first significant digit shared by both.

    See unit tests for examples.
    """
    min_bits = minimum.normalize().as_tuple()
    max_bits = maximum.normalize().as_tuple()

    max_digits = max(
        len(min_bits.digits) + min_bits.exponent,
        len(max_bits.digits) + max_bits.exponent
    )

    # Whole number rounding
    if max_digits > 0:
        multiplier = Decimal('10') ** (max_digits - 1)

        min_fraction = (minimum / multiplier).to_integral_value(rounding=ROUND_FLOOR)
        max_fraction = (maximum / multiplier).to_integral_value(rounding=ROUND_CEILING)

        return (
            min_fraction * multiplier,
            max_fraction * multiplier
        )

    max_exponent = max(min_bits.exponent, max_bits.exponent)

    # Fractional rounding
    q = Decimal('10') ** (max_exponent + 1)

    return (
        minimum.quantize(q, rounding=ROUND_FLOOR).normalize(),
        maximum.quantize(q, rounding=ROUND_CEILING).normalize()
    )


def letter_name(index):
    """
    Given a column index, assign a "letter" column name equivalent to
    Excel. For example, index ``4`` would return ``E``.
    Index ``30`` would return ``EE``.
    """
    letters = string.ascii_lowercase
    count = len(letters)

    return letters[index % count] * ((index // count) + 1)


def parse_object(obj, path=''):
    """
    Recursively parse JSON-like Python objects as a dictionary of paths/keys
    and values.

    Inspired by JSONPipe (https://github.com/dvxhouse/jsonpipe).
    """
    if isinstance(obj, dict):
        iterator = obj.items()
    elif isinstance(obj, (list, tuple)):
        iterator = enumerate(obj)
    else:
        return {path.strip('/'): obj}

    d = OrderedDict()

    for key, value in iterator:
        key = six.text_type(key)
        d.update(parse_object(value, path + key + '/'))

    return d


def issequence(obj):
    """
    Returns :code:`True` if the given object is an instance of
    :class:`.Sequence` that is not also a string.
    """
    return isinstance(obj, Sequence) and not isinstance(obj, six.string_types)
