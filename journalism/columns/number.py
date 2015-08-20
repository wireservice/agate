#!/usr/bin/env python

from collections import defaultdict
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
    else:
        half = length // 2
        a = data_sorted[half - 1]
        b = data_sorted[half]

    return (a + b) / 2
    
class NumberColumn(Column):
    """
    A column containing numeric data.

    All data is represented by the :class:`decimal.Decimal` class.'
    """
    def sum(self):
        """
        Compute the sum of this column.

        :returns: :class:`decimal.Decimal`.
        """
        return sum(self._data_without_nulls())

    def min(self):
        """
        Compute the minimum value of this column.

        :returns: :class:`decimal.Decimal`.
        """
        return min(self._data_without_nulls())

    def max(self):
        """
        Compute the maximum value of this column.

        :returns: :class:`decimal.Decimal`.
        """
        return max(self._data_without_nulls())

    @no_null_computations
    def mean(self):
        """
        Compute the mean value of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        return self.sum() / len(self)

    @no_null_computations
    def median(self):
        """
        Compute the median value of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        return _median(self._data_sorted())

    @no_null_computations
    def mode(self):
        """
        Compute the mode value of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        data = self._data()
        state = defaultdict(int)

        for n in data:
            state[n] += 1

        return max(state.keys(), key=lambda x: state[x])

    @no_null_computations
    def variance(self):
        """
        Compute the variance of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        data = self._data()
        mean = self.mean()

        return sum((n - mean) ** 2 for n in data) / len(data)

    @no_null_computations
    def stdev(self):
        """
        Compute the standard of deviation of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        return self.variance().sqrt()

    @no_null_computations
    def mad(self):
        """
        Compute the `median absolute deviation <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
        of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        data = self._data_sorted()
        m = _median(data)

        return _median(tuple(abs(n - m) for n in data))

    @no_null_computations
    def quantiles(self, count):
        """
        Compute a list of values which divide the column data in some number
        of equal sized groups.

        :param count: The number of quantiles to generate.
        :returns: A list of `count` quantile values.
        :raises: :exc:`.NullComputationError`
        """
        data = self._data_sorted()

        if len(data) < count:
            raise ValueError('Column must contain at least as many rows as the number of quantiles you wish to generate.')

        breaks = []

        for i in range(1, count + 1):
            k = (len(data) - 1) * (Decimal(i) / count)

            # Determine if this break falls precisely on a value
            f = int(math.floor(k))
            c = int(math.ceil(k))

            print i, data[int(k)], data[f], data[c]

            if f == c:
                breaks.append(data[int(k)])
                continue

            # Otherwise split the difference
            d0 = data[f] * (c - k)
            d1 = data[c] * (k - f)

            breaks.append(d0 + d1)

        return breaks

    @no_null_computations
    def quartiles(self):
        """
        Compute quartiles for this column of data.

        This method is equivalent to ``NumberColumn.quantiles(4)``.

        :raises: :exc:`.NullComputationError`
        """
        return self.quantiles(4)

    @no_null_computations
    def percentiles(self):
        """
        Compute percentiles for this column of data.

        This method is equivalent to ``NumberColumn.quantiles(100)``.

        :raises: :exc:`.NullComputationError`
        """
        return self.quantiles(100)

class NumberColumnSet(ColumnSet):
    """
    See :class:`ColumnSet` and :class:`NumberColumn`.
    """
    def __init__(self, *args, **kwargs):
        super(NumberColumnSet, self).__init__(*args, **kwargs)

        self.sum = ColumnMethodProxy(self, 'sum')
        self.min = ColumnMethodProxy(self, 'min')
        self.max = ColumnMethodProxy(self, 'max')
        self.mean = ColumnMethodProxy(self, 'mean')
        self.median = ColumnMethodProxy(self, 'median')
        self.mode = ColumnMethodProxy(self, 'mode')
        self.variance = ColumnMethodProxy(self, 'variance')
        self.stdev = ColumnMethodProxy(self, 'stdev')
        self.mad = ColumnMethodProxy(self, 'mad')
        self.percentile = ColumnMethodProxy(self, 'percentile')

class ColumnQuantiles(object):
    pass

class ColumnQuartiles(ColumnQuantiles):
    pass

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
