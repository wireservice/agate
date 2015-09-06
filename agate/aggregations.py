#!/usr/bin/env python

"""
This module contains the :class:`Aggregation` class and its various subclasses.
Each of these classes processes a column's data and returns a single value. For
instance, :class:`Mean`, when applied to a :class:`.NumberColumn`, returns a
single :class:`decimal.Decimal` value which is the average of all values in that column.

Aggregations are applied to instances of :class:`.Column` using the
:meth:`.Column.aggregate` method. Typically, the column is first retrieved using
the :attr:`.Table.columns` attribute.

Aggregations can also be applied to instances of :class:`.TableSet` using the
:meth:`.Tableset.aggregate` method, in which case the result will be a new
:class:`.Table` with a column for each aggregation and a row for each table in
the set.
"""

from collections import defaultdict
import datetime

from agate.column_types import *
from agate.columns import *
from agate.exceptions import *

class Aggregation(object): #pragma: no cover
    """
    Base class defining an operation that can be performed on a column either
    to yield an individual value or as part of a :class:`.TableSet` aggregate.
    """
    def get_aggregate_column_type(self, column):
        """
        Get the correct column type for an new column based on this aggregation.
        """
        raise NotImplementedError()

    def run(self, column):
        """
        Execute this aggregation on a given column and return the result.
        """
        raise NotImplementedError()

class HasNulls(Aggregation):
    """
    Returns :code:`True` if the column contains null values.
    """
    def get_aggregate_column_type(self, column):
        return BooleanType()

    def run(self, column):
        """
        :returns: :class:`bool`
        """
        return column.has_nulls()

class Any(Aggregation):
    """
    Returns :code:`True` if any value in a column passes a truth test. The
    truth test may be omitted when testing a :class:`.BooleanColumn`.

    :param test: A function that takes a value and returns :code:`True`
        or :code:`False`.
    """
    def __init__(self, test=None):
        self._test = test

    def get_aggregate_column_type(self, column):
        return BooleanType()

    def run(self, column):
        """
        :returns: :class:`bool`
        """
        data = column.get_data()

        if isinstance(column, BooleanColumn):
            return any(data)
        elif not self._test:
            raise ValueError('You must supply a test function for non-BooleanColumn.')

        return any(self._test(d) for d in data)

class All(Aggregation):
    """
    Returns :code:`True` if all values in a column pass a truth test. The truth
    test may be omitted when testing a :class:`.BooleanColumn`.

    :param test: A function that takes a value and returns :code:`True`
        or :code:`False`.
    """
    def __init__(self, test=None):
        self._test = test

    def get_aggregate_column_type(self, column):
        return BooleanType()

    def run(self, column):
        """
        :returns: :class:`bool`
        """
        data = column.get_data()

        if isinstance(column, BooleanColumn):
            return all(data)
        elif not self._test:
            raise ValueError('You must supply a test function for non-BooleanColumn.')

        return all(self._test(d) for d in data)

class Length(Aggregation):
    """
    Count the total number of values in the column.

    Equivalent to Python's :func:`len` function.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`int`
        """
        return len(column)

class Count(Aggregation):
    """
    Count the number of times a specific value occurs in a column.

    If you want to count the total number of values in a column use
    :class:`Length`.

    :param value: The value to be counted.
    """
    def __init__(self, value):
        self._value = value

    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`int`
        """
        return column.get_data().count(self._value)

class Min(Aggregation):
    """
    Compute the minimum value in a column. May be applied to
    :class:`.DateTimeColumn` and :class:`.NumberColumn`.
    """
    def get_aggregate_column_type(self, column):
        if isinstance(column, DateTimeColumn):
            return DateTimeType()
        elif isinstance(column, NumberColumn):
            return NumberType()

        raise UnsupportedAggregationError(self, column)

    def run(self, column):
        """
        :returns: :class:`datetime.date`
        """
        if not (isinstance(column, DateTimeColumn) or isinstance(column, NumberColumn)):
            raise UnsupportedAggregationError(self, column)

        return min(column.get_data_without_nulls())

class Max(Aggregation):
    """
    Compute the maximum value in a column. May be applied to
    :class:`.DateTimeColumn` and :class:`.NumberColumn`.
    """
    def get_aggregate_column_type(self, column):
        if isinstance(column, DateTimeColumn):
            return DateTimeType()
        elif isinstance(column, NumberColumn):
            return NumberType()

    def run(self, column):
        """
        :returns: :class:`datetime.date`
        """
        if not (isinstance(column, DateTimeColumn) or isinstance(column, NumberColumn)):
            raise UnsupportedAggregationError(self, column)

        return max(column.get_data_without_nulls())

class Sum(Aggregation):
    """
    Compute the sum of a column.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        return column.sum()

class Mean(Aggregation):
    """
    Compute the mean value of a column.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        return column.mean()

class Median(Aggregation):
    """
    Compute the median value of a column.

    This is the 50th percentile. See :class:`Percentiles` for implementation
    details.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        return column.median()

class Mode(Aggregation):
    """
    Compute the mode value of a column.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        if column.has_nulls():
            raise NullCalculationError

        data = column.get_data()
        state = defaultdict(int)

        for n in data:
            state[n] += 1

        return max(state.keys(), key=lambda x: state[x])

class IQR(Aggregation):
    """
    Compute the inter-quartile range of a column.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        percentiles = column.percentiles()

        return percentiles[75] - percentiles[25]

class Variance(Aggregation):
    """
    Compute the sample variance of a column.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        return column.variance()

class PopulationVariance(Variance):
    """
    Compute the population variance of a column.
    """
    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        return column.population_variance()

class StDev(Aggregation):
    """
    Compute the sample standard of deviation of a column.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        return column.variance().sqrt()

class PopulationStDev(StDev):
    """
    Compute the population standard of deviation of a column.
    """
    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        return column.population_variance().sqrt()

class MAD(Aggregation):
    """
    Compute the `median absolute deviation <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
    of a column.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def _median(self, data_sorted):
        length = len(data_sorted)

        if length % 2 == 1:
            return data_sorted[((length + 1) // 2) - 1]

        half = length // 2
        a = data_sorted[half - 1]
        b = data_sorted[half]

        return (a + b) / 2

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column, NumberColumn):
            raise UnsupportedAggregationError(self, column)

        if column.has_nulls():
            raise NullCalculationError

        data = column.get_data_sorted()
        m = column.percentiles()[50]

        return self._median(tuple(abs(n - m) for n in data))

class MaxLength(Aggregation):
    """
    Calculates the longest string in a column.
    """
    def get_aggregate_column_type(self, column):
        return NumberType()

    def run(self, column):
        """
        :returns: :class:`int`.
        """
        if not isinstance(column, TextColumn):
            raise UnsupportedAggregationError(self, column)

        return max([len(d) for d in column.get_data_without_nulls()])
