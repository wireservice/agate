#!/usr/bin/env python

from collections import defaultdict, Sequence
import math

try:
    from cdecimal import Decimal, InvalidOperation
except ImportError: #pragma: no cover
    from decimal import Decimal, InvalidOperation

import six

from journalism.columns.base import *
from journalism.exceptions import CastError

def _median(data_sorted):
    """
    Compute the median value of a sequence of values.

    :param data_sorted: A sorted sequence of :class:`decimal.Decimal`.
    :returns: :class:`decimal.Decimal`.
    """
    length = len(data_sorted)

    if length % 2 == 1:
        return data_sorted[((length + 1) // 2) - 1]

    half = length // 2
    a = data_sorted[half - 1]
    b = data_sorted[half]

    return (a + b) / 2

def no_null_computations(func):
    """
    Decorator for :class:`.ColumnOperation` functions that prevents illogical
    computations on columns containing nulls.
    """
    @wraps(func)
    def check(op, *args, **kwargs):
        if op._column.has_nulls():
            raise NullComputationError

        return func(op, *args, **kwargs)

    return check

class NumberType(ColumnType):
    """
    Column type for :class:`NumberColumn`.
    """
    def cast(self, d):
        """
        Cast a single value to a :class:`decimal.Decimal`.

        :returns: :class:`decimal.Decimal` or :code:`None`.
        :raises: :exc:`.CastError`
        """
        if isinstance(d, Decimal) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.replace(',' ,'').strip()

            if d.lower() in NULL_VALUES:
                return None

        if isinstance(d, float):
            raise CastError('Can not convert float to Decimal for NumberColumn. Convert data to string first!')

        try:
            return Decimal(d)
        except InvalidOperation:
            raise CastError('Can not convert value "%s" to Decimal for NumberColumn.' % d)

    def _create_column(self, table, index):
        return NumberColumn(table, index)

    def _create_column_set(self, tableset, index):
        return NumberColumnSet(tableset, index)

class NumberColumn(Column):
    """
    A column containing numeric data.

    All data is represented by the :class:`decimal.Decimal` class.'
    """
    def __init__(self, *args, **kwargs):
        super(NumberColumn, self).__init__(*args, **kwargs)

        self._cached_percentiles = None
        self._cached_quartiles = None

        self.sum = SumOperation(self)
        self.min = MinOperation(self)
        self.max = MaxOperation(self)
        self.mean = MeanOperation(self)
        self.median = MedianOperation(self)
        self.mode = ModeOperation(self)
        self.variance = VarianceOperation(self)
        self.stdev = StdevOperation(self)
        self.mad = MadOperation(self)

    def percentiles(self):
        """
        Compute percentiles for this column of data.

        :returns: :class:`Percentiles`.
        :raises: :exc:`.NullComputationError`
        """
        if self.has_nulls():
            raise NullComputationError

        if self._cached_percentiles:
            return self._cached_percentiles

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

class SumOperation(ColumnOperation):
    """
    Compute the sum of this column.

    :returns: :class:`decimal.Decimal`.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self):
        return sum(self._column._data_without_nulls())

class MinOperation(ColumnOperation):
    """
    Compute the minimum value of this column.

    :returns: :class:`decimal.Decimal`.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self):
        return min(self._column._data_without_nulls())

class MaxOperation(ColumnOperation):
    """
    Compute the maximum value of this column.

    :returns: :class:`decimal.Decimal`.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self):
        return max(self._column._data_without_nulls())

class MeanOperation(ColumnOperation):
    """
    Compute the mean value of this column.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    @no_null_computations
    def __call__(self):
        return self._column.sum() / len(self._column)

class MedianOperation(ColumnOperation):
    """
    Compute the median value of this column.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    @no_null_computations
    def __call__(self):
        return _median(self._column._data_sorted())

class ModeOperation(ColumnOperation):
    """
    Compute the mode value of this column.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    @no_null_computations
    def __call__(self):
        data = self._column._data()
        state = defaultdict(int)

        for n in data:
            state[n] += 1

        return max(state.keys(), key=lambda x: state[x])

class VarianceOperation(ColumnOperation):
    """
    Compute the variance of this column.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    @no_null_computations
    def __call__(self):
        data = self._column._data()
        mean = self._column.mean()

        return sum((n - mean) ** 2 for n in data) / len(data)

class StdevOperation(ColumnOperation):
    """
    Compute the standard of deviation of this column.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    @no_null_computations
    def __call__(self):
        return self._column.variance().sqrt()

class MadOperation(ColumnOperation):
    """
    Compute the `median absolute deviation <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
    of this column.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    @no_null_computations
    def __call__(self):
        data = self._column._data_sorted()
        m = _median(data)

        return _median(tuple(abs(n - m) for n in data))

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

    def locate(self, value):
        """
        Identify which percentile a given value is part of.
        """
        i = 1

        while value >= self._quantiles[i]:
            i += 1

        return i - 1

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
