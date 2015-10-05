#!/usr/bin/env python

"""
This module contains the :class:`Aggregation` class and its various subclasses.
Each of these classes processes a column's data and returns some value(s). For
instance, :class:`Mean`, when applied to a column containing :class:`.Number`
data, returns a single :class:`decimal.Decimal` value which is the average of
all values in that column.

Aggregations are applied to instances of :class:`.Column` using the
:meth:`.Column.aggregate` method. Typically, the column is first retrieved using
the :attr:`.Table.columns` attribute.

Most aggregations can also be applied to instances of :class:`.TableSet` using
the :meth:`.Tableset.aggregate` method, in which case the result will be a new
:class:`.Table` with a column for each aggregation and a row for each table in
the set.
"""

from collections import defaultdict
import math

from agate.data_types import Boolean, Date, DateTime, Number, Text
from agate.exceptions import DataTypeError, NullCalculationError, UnsupportedAggregationError
from agate.utils import Quantiles, max_precision, median

class Aggregation(object): #pragma: no cover
    """
    Base class defining an operation that can be executed on a column using
    :meth:`.Table.aggregate` or on a set of columns using
    :class:`.TableSet.aggregate`.
    """
    def get_cache_key(self):
        """
        Aggregations can optionally define a cache key that uniquely identifies
        this operation. If they do they future invocations of this aggregation
        with the same cache key applied to the same column will use the
        cached value.
        """
        return None

    def get_aggregate_data_type(self, column):
        """
        Get the data type that should be used when using this aggregation with
        a :class:`.TableSet` to produce a new column.

        Should raise :class:`.UnsupportedAggregationError` if this column does
        not support aggregation into a :class:`.TableSet`. (For example, if it
        does not return a single value.)
        """
        raise UnsupportedAggregationError()

    def run(self, column):
        """
        Execute this aggregation on a given column and return the result.
        """
        raise NotImplementedError()

class HasNulls(Aggregation):
    """
    Returns :code:`True` if the column contains null values.
    """
    def get_aggregate_data_type(self, column):
        return Boolean()

    def get_cache_key(self):
        return 'HasNulls'

    def run(self, column):
        """
        :returns: :class:`bool`
        """
        return None in column.get_data()

class Any(Aggregation):
    """
    Returns :code:`True` if any value in a column passes a truth test. The
    truth test may be omitted when testing :class:`.Boolean` data.

    :param test: A function that takes a value and returns :code:`True`
        or :code:`False`.
    """
    def __init__(self, test=None):
        self._test = test

    def get_aggregate_data_type(self, column):
        return Boolean()

    def run(self, column):
        """
        :returns: :class:`bool`
        """
        data = column.get_data()

        if isinstance(column.data_type, Boolean):
            return any(data)
        elif not self._test:
            raise ValueError('You must supply a test function for columns containing non-Boolean data.')

        return any(self._test(d) for d in data)

class All(Aggregation):
    """
    Returns :code:`True` if all values in a column pass a truth test. The truth
    test may be omitted when testing :class:`.Boolean` data.

    :param test: A function that takes a value and returns :code:`True`
        or :code:`False`.
    """
    def __init__(self, test=None):
        self._test = test

    def get_aggregate_data_type(self, column):
        return Boolean()

    def run(self, column):
        """
        :returns: :class:`bool`
        """
        data = column.get_data()

        if isinstance(column.data_type, Boolean):
            return all(data)
        elif not self._test:
            raise ValueError('You must supply a test function for columns containing non-Boolean data.')

        return all(self._test(d) for d in data)

class Length(Aggregation):
    """
    Count the total number of values in the column.

    Equivalent to calling :func:`len` on a :class:`.Column`.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'Length'

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

    :param value: Any value to be counted, including :code:`None`.
    """
    def __init__(self, value):
        self._value = value

    def get_aggregate_data_type(self, column):
        return Number()

    def run(self, column):
        """
        :returns: :class:`int`
        """
        return column.get_data().count(self._value)

class Min(Aggregation):
    """
    Compute the minimum value in a column. May be applied to columns containing
    :class:`.DateTime` or :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        if isinstance(column.data_type, Number) or \
            isinstance(column.data_type, Date) or \
            isinstance(column.data_type, DateTime):
            return column.data_type

    def run(self, column):
        """
        :returns: :class:`datetime.date`
        """
        if not (isinstance(column.data_type, Number) or \
            isinstance(column.data_type, Date) or \
            isinstance(column.data_type, DateTime)):
            raise DataTypeError('Min can only be applied to columns containing DateTime orNumber data.')

        return min(column.get_data_without_nulls())

class Max(Aggregation):
    """
    Compute the maximum value in a column. May be applied to columns containing
    :class:`.DateTime` or :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        if isinstance(column.data_type, Number) or \
            isinstance(column.data_type, Date) or \
            isinstance(column.data_type, DateTime):
            return column.data_type

    def run(self, column):
        """
        :returns: :class:`datetime.date`
        """
        if not (isinstance(column.data_type, Number) or \
            isinstance(column.data_type, Date) or \
            isinstance(column.data_type, DateTime)):
            raise DataTypeError('Max can only be applied to columns containing DateTime or Number data.')

        return max(column.get_data_without_nulls())

class MaxPrecision(Aggregation):
    """
    Compute the most decimal places present for any value in this column.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'MaxPrecision'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('MaxPrecision can only be applied to columns containing Number data.')

        return max_precision(column.get_data_without_nulls())

class Sum(Aggregation):
    """
    Compute the sum of a column containing :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'Sum'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('Sum can only be applied to columns containing Number data.')

        return sum(column.get_data_without_nulls())

class Mean(Aggregation):
    """
    Compute the mean value of a column containing :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'Mean'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('Mean can only be applied to columns containing Number data.')

        if column.aggregate(HasNulls()):
            raise NullCalculationError

        return column.aggregate(Sum()) / len(column)

class Median(Aggregation):
    """
    Compute the median value of a column containing :class:`.Number` data.

    This is the 50th percentile. See :class:`Percentiles` for implementation
    details.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'Median'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('Median can only be applied to columns containing Number data.')

        if column.aggregate(HasNulls()):
            raise NullCalculationError

        return column.aggregate(Percentiles())[50]

class Mode(Aggregation):
    """
    Compute the mode value of a column containing :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'Mode'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('Mode can only be applied to columns containing Number data.')

        if column.aggregate(HasNulls()):
            raise NullCalculationError

        data = column.get_data()
        state = defaultdict(int)

        for n in data:
            state[n] += 1

        return max(state.keys(), key=lambda x: state[x])

class IQR(Aggregation):
    """
    Compute the interquartile range of a column containing
    :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'IQR'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('IQR can only be applied to columns containing Number data.')

        if column.aggregate(HasNulls()):
            raise NullCalculationError

        percentiles = column.aggregate(Percentiles())

        return percentiles[75] - percentiles[25]

class Variance(Aggregation):
    """
    Compute the sample variance of a column containing
    :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'Variance'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('Variance can only be applied to columns containing Number data.')

        if column.aggregate(HasNulls()):
            raise NullCalculationError

        data = column.get_data()
        mean = column.aggregate(Mean())

        return sum((n - mean) ** 2 for n in data) / (len(column) - 1)

class PopulationVariance(Variance):
    """
    Compute the population variance of a column containing
    :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'PopulationVariance'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('PopulationVariance can only be applied to columns containing Number data.')

        if column.aggregate(HasNulls()):
            raise NullCalculationError

        data = column.get_data()
        mean = column.aggregate(Mean())

        return sum((n - mean) ** 2 for n in data) / len(column)

class StDev(Aggregation):
    """
    Compute the sample standard of deviation of a column containing
    :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'StDev'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('StDev can only be applied to columns containing Number data.')

        return column.aggregate(Variance()).sqrt()

class PopulationStDev(StDev):
    """
    Compute the population standard of deviation of a column containing
    :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'PopulationStDev'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('PopulationStDev can only be applied to columns containing Number data.')

        return column.aggregate(PopulationVariance()).sqrt()

class MAD(Aggregation):
    """
    Compute the `median absolute deviation <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
    of a column containing :class:`.Number` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'MAD'

    def run(self, column):
        """
        :returns: :class:`decimal.Decimal`.
        """
        if not isinstance(column.data_type, Number):
            raise DataTypeError('MAD can only be applied to columns containing Number data.')

        if column.aggregate(HasNulls()):
            raise NullCalculationError

        data = column.get_data_sorted()
        m = column.aggregate(Percentiles())[50]

        return median(tuple(abs(n - m) for n in data))

class Percentiles(Aggregation):
    """
    Divides a :class:`.Number` column into 100 equal-size groups using the
    "CDF" method.

    See `this explanation <http://www.amstat.org/publications/jse/v14n3/langford.html>`_
    of the various methods for computing percentiles.

    "Zeroth" (min value) and "Hundredth" (max value) percentiles are included
    for reference and intuitive indexing.

    A reference implementation was provided by
    `pycalcstats <https://code.google.com/p/pycalcstats/>`_.

    This aggregation can not be applied to a :class:`.TableSet`.
    """
    def get_cache_key(self):
        return 'Percentiles'

    def run(self, column):
        """
        :returns: An array of :class:`decimal.Decimal`.
        """
        if column.aggregate(HasNulls()):
            raise NullCalculationError

        data = column.get_data_sorted()

        # Zeroth percentile is first datum
        quantiles = [data[0]]

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

            quantiles.append(value)

        # Hundredth percentile is final datum
        quantiles.append(data[-1])

        return Quantiles(quantiles)

class Quartiles(Aggregation):
    """
    The quartiles of a :class:`.Number` column based on the 25th, 50th and
    75th percentiles.

    "Zeroth" (min value) and "Fourth" (max value) quartiles are included for
    reference and intuitive indexing.

    See :class:`Percentiles` for implementation details.

    This aggregation can not be applied to a :class:`.TableSet`.
    """
    def get_cache_key(self):
        return 'Quartiles'

    def run(self, column):
        percentiles = column.aggregate(Percentiles())

        return Quantiles([percentiles[i] for i in range(0, 101, 25)])

class Quintiles(Aggregation):
    """
    The quintiles of a column based on the 20th, 40th, 60th and 80th
    percentiles.

    "Zeroth" (min value) and "Fifth" (max value) quintiles are included for
    reference and intuitive indexing.

    See :class:`Percentiles` for implementation details.

    This aggregation can not be applied to a :class:`.TableSet`.
    """
    def get_cache_key(self):
        return 'Quintiles'

    def run(self, column):
        percentiles = column.aggregate(Percentiles())

        return Quantiles([percentiles[i] for i in range(0, 101, 20)])

class Deciles(Aggregation):
    """
    The deciles of a column based on the 10th, 20th ... 90th percentiles.

    "Zeroth" (min value) and "Tenth" (max value) deciles are included for
    reference and intuitive indexing.

    See :class:`Percentiles` for implementation details.

    This aggregation can not be applied to a :class:`.TableSet`.
    """
    def get_cache_key(self):
        return 'Deciles'

    def run(self, column):
        percentiles = column.aggregate(Percentiles())

        return Quantiles([percentiles[i] for i in range(0, 101, 10)])

class MaxLength(Aggregation):
    """
    Calculates the longest string in a column containing :class:`.Text` data.
    """
    def get_aggregate_data_type(self, column):
        return Number()

    def get_cache_key(self):
        return 'MaxLength'

    def run(self, column):
        """
        :returns: :class:`int`.
        """
        if not isinstance(column.data_type, Text):
            raise DataTypeError('MaxLength can only be applied to columns containing Text data.')

        return max([len(d) for d in column.get_data_without_nulls()])
