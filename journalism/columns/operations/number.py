#!/usr/bin/env python

from collections import defaultdict
from functools import wraps

from journalism.column_types import NumberType
from journalism.columns.operations.base import ColumnOperation
from journalism.exceptions import NullComputationError

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

class Sum(ColumnOperation):
    """
    Compute the sum of this column.

    :returns: :class:`decimal.Decimal`.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self):
        return sum(self._column._data_without_nulls())

class Min(ColumnOperation):
    """
    Compute the minimum value of this column.

    :returns: :class:`decimal.Decimal`.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self):
        return min(self._column._data_without_nulls())

class Max(ColumnOperation):
    """
    Compute the maximum value of this column.

    :returns: :class:`decimal.Decimal`.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self):
        return max(self._column._data_without_nulls())

class Mean(ColumnOperation):
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

class Median(ColumnOperation):
    """
    Compute the median value of this column.

    This is the 50th percentile. See :class:`Percentiles` for implementation
    details.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    @no_null_computations
    def __call__(self):
        return self._column.percentiles()[50]

class Mode(ColumnOperation):
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

class IQR(ColumnOperation):
    """
    Compute the inter-quartile range of this column.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    @no_null_computations
    def __call__(self):
        percentiles = self._column.percentiles()

        return percentiles[75] - percentiles[25]

class Variance(ColumnOperation):
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

class Stdev(ColumnOperation):
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

class MAD(ColumnOperation):
    """
    Compute the `median absolute deviation <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
    of this column.

    :returns: :class:`decimal.Decimal`.
    :raises: :exc:`.NullComputationError`
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def _median(self, data_sorted):
        length = len(data_sorted)

        if length % 2 == 1:
            return data_sorted[((length + 1) // 2) - 1]

        half = length // 2
        a = data_sorted[half - 1]
        b = data_sorted[half]

        return (a + b) / 2

    @no_null_computations
    def __call__(self):
        data = self._column._data_sorted()
        m = self._column.percentiles()[50]

        return self._median(tuple(abs(n - m) for n in data))
