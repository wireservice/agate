#!/usr/bin/env python

from collections import Sequence
import math

import six

from journalism.columns.base import Column
from journalism.exceptions import NullComputationError

class NumberColumn(Column):
    """
    A column containing numeric data.

    All data is represented by the :class:`decimal.Decimal` class.
    """
    def __init__(self, *args, **kwargs):
        super(NumberColumn, self).__init__(*args, **kwargs)

        self._cached_percentiles = None

    def percentiles(self):
        """
        Compute percentiles for this column of data.

        :returns: :class:`Percentiles`.
        :raises: :exc:`.NullComputationError`
        """
        if self._cached_percentiles is None:
            if self._has_nulls():
                raise NullComputationError

            self._cached_percentiles = Percentiles(self)

        return self._cached_percentiles

    def quartiles(self):
        """
        Compute quartiles for this column of data.

        :returns: :class:`Quartiles`.
        :raises: :exc:`.NullComputationError`
        """
        return Quartiles(self.percentiles())

    def quintiles(self):
        """
        Compute quintiles for this column of data.

        :returns: :class:`Quintiles`.
        :raises: :exc:`.NullComputationError`
        """
        return Quintiles(self.percentiles())

    def deciles(self):
        """
        Compute deciles for this column of data.

        :returns: :class:`Deciles`.
        :raises: :exc:`.NullComputationError`
        """
        return Deciles(self.percentiles())

class Quantiles(Sequence):
    """
    Base class defining the interface for various quantile implementations.
    """
    def __init__(self):
        self._quantiles = []

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
        Identify which percentile a given value is part of.
        """
        i = 0

        if value < self._quantiles[0]:
            raise ValueError('Value is less than minimum percentile value.')

        if value > self._quantiles[-1]:
            raise ValueError('Value is greater than maximum percentile value.')

        if value == self._quantiles[-1]:
            return len(self._quantiles) - 1

        while value >= self._quantiles[i + 1]:
            i += 1

        return i

class Percentiles(Quantiles):
    """
    Divides column data into 100 equal-size groups using the "CDF" method.

    See `this explanation <http://www.amstat.org/publications/jse/v14n3/langford.html>`_
    of the various methods for computing percentiles.

    "Zeroth" (min value) and "Hundredth" (max value) percentiles are included
    for reference and intuitive indexing.

    A reference implementation was provided by
    `pycalcstats <https://code.google.com/p/pycalcstats/>`_.
    """
    def __init__(self, column):
        super(Percentiles, self).__init__()

        data = column._data_sorted()

        if len(data) == 0:
            raise ValueError('Column does not contain data.')

        # Zeroth percentile is first datum
        self._quantiles = [data[0]]

        for percentile in range(1, 100):
            k = len(data) * (float(percentile) / 100)

            low = max(1, int(math.ceil(k)))
            high = min(len(data), int(math.floor(k + 1)))

            # No remainder
            if low == high:
                value = data[low - 1]
            # Remainder
            else:
                value = (data[low - 1] + data[high - 1]) / 2

            self._quantiles.append(value)

        # Hundredth percentile is final datum
        self._quantiles.append(data[-1])

class Quartiles(Quantiles):
    """
    The quartiles of a column based on the 25th, 50th and 75th percentiles.

    "Zeroth" (min value) and "Fourth" (max value) quartiles are included for
    reference and intuitive indexing.

    See :class:`Percentiles` for implementation details.
    """
    def __init__(self, percentiles):
        self._quantiles = [percentiles[i] for i in range(0, 101, 25)]

class Quintiles(Quantiles):
    """
    The quintiles of a column based on the 20th, 40th, 60th and 80th
    percentiles.

    "Zeroth" (min value) and "Fifth" (max value) quintiles are included for
    reference and intuitive indexing.

    See :class:`Percentiles` for implementation details.
    """
    def __init__(self, percentiles):
        self._quantiles = [percentiles[i] for i in range(0, 101, 20)]

class Deciles(Quantiles):
    """
    The deciles of a column based on the 10th, 20th ... 90th percentiles.

    "Zeroth" (min value) and "Tenth" (max value) deciles are included for
    reference and intuitive indexing.

    See :class:`Percentiles` for implementation details.
    """
    def __init__(self, percentiles):
        self._quantiles = [percentiles[i] for i in range(0, 101, 10)]
