#!/usr/bin/env python

"""
This module contains the :class:`Aggregation` class and its various subclasses.
Each of these classes processes a column's data and returns some value(s). For
instance, :class:`Mean`, when applied to a column containing :class:`.Number`
data, returns a single :class:`decimal.Decimal` value which is the average of
all values in that column.

Aggregations are applied to single columns using the :meth:`.Table.aggregate`
method. There result is a single value if a single aggregation was applied, or
a tuple of values if a sequence of aggregations was applied.

Aggregations are applied to instances of :class:`.TableSet` using the
:meth:`.Tableset.aggregate` method. The result will be a new :class:`.Table`
with a column for each aggregation and a row for each table in the set.
"""

from collections import defaultdict
import math

import six

from agate.data_types import Boolean, Date, DateTime, Number, Text
from agate.exceptions import DataTypeError, UnsupportedAggregationError
from agate.utils import Quantiles, default, max_precision, median
from agate.warns import warn_null_calculation

@six.python_2_unicode_compatible
class Aggregation(object):  # pragma: no cover
    """
    An operation that takes a table and produces a single value summarizing
    one of it's columns. Aggregations are invoked with
    :class:`.TableSet.aggregate`.

    When implementing a custom subclass, ensure that the values returned by
    :meth:`run` are of the type specified by :meth:`get_aggregate_data_type`.
    This can be ensured by using the :meth:`.DataType.cast` method. See
    :class:`Formula` for an example.
    """
    def __str__(self):
        """
        String representation of this column. May be used as a column name in
        generated tables.
        """
        return self.__class__.__name__

    def get_aggregate_data_type(self, table):
        """
        Get the data type that should be used when using this aggregation with
        a :class:`.TableSet` to produce a new column.

        Should raise :class:`.UnsupportedAggregationError` if this column does
        not support aggregation into a :class:`.TableSet`. (For example, if it
        does not return a single value.)
        """
        raise UnsupportedAggregationError()

    def validate(self, table):
        """
        Perform any checks necessary to verify this aggregation can run on the
        provided table without errors. This is called by
        :meth:`.Table.aggregate` before :meth:`run`.
        """
        pass

    def run(self, table):
        """
        Execute this aggregation on a given column and return the result.
        """
        raise NotImplementedError()


class Summary(Aggregation):
    """
    An aggregation that can apply an arbitrary function to a column.

    :param column_name:
        The column being summarized.
    :param data_type:
        The return type of this aggregation.
    :param func:
        A function which will be passed the column for processing.
    """
    def __init__(self, column_name, data_type, func):
        self._column_name = column_name
        self._data_type = data_type
        self._func = func

    def get_aggregate_data_type(self, table):
        return self._data_type

    def run(self, table):
        return self._func(table.columns[self._column_name])


class HasNulls(Aggregation):
    """
    Returns :code:`True` if the column contains null values.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Boolean()

    def run(self, table):
        return None in table.columns[self._column_name].values()


class Any(Aggregation):
    """
    Returns :code:`True` if any value in a column passes a truth test. The
    truth test may be omitted when testing :class:`.Boolean` data.

    :param test:
        A function that takes a value and returns `True` or `False`.
    """
    def __init__(self, column_name, test=None):
        self._column_name = column_name
        self._test = test

    def get_aggregate_data_type(self, table):
        return Boolean()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Boolean) and not self._test:
            raise ValueError('You must supply a test function for columns containing non-Boolean data.')

    def run(self, table):
        column = table.columns[self._column_name]
        data = column.values()

        if isinstance(column.data_type, Boolean):
            return any(data)

        return any(self._test(d) for d in data)


class All(Aggregation):
    """
    Returns :code:`True` if all values in a column pass a truth test. The truth
    test may be omitted when testing :class:`.Boolean` data.

    :param test:
        A function that takes a value and returns `True` or `False`.
    """
    def __init__(self, column_name, test=None):
        self._column_name = column_name
        self._test = test

    def get_aggregate_data_type(self, table):
        return Boolean()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Boolean) and not self._test:
            raise ValueError('You must supply a test function for columns containing non-Boolean data.')

    def run(self, table):
        """
        :returns:
            :class:`bool`
        """
        column = table.columns[self._column_name]
        data = column.values()

        if isinstance(column.data_type, Boolean):
            return all(data)

        return all(self._test(d) for d in data)


class Count(Aggregation):
    """
    Count values. If no arguments are specified, this is simply a count of the
    number of rows in the table. If only :code:`column_name` is specified, this
    will count the number of non-null values in that column. If both
    :code:`column_name` and :code:`value` are specified, then it will count
    occurrences of a specific value in the specified column will be counted.

    :param column_name:
        A column to count values in.
    :param value:
        Any value to be counted, including :code:`None`.
    """
    def __init__(self, column_name=None, value=default):
        self._column_name = column_name
        self._value = value

    def get_aggregate_data_type(self, table):
        return Number()

    def run(self, table):
        if self._column_name is not None:
            if self._value is not default:
                return table.columns[self._column_name].values().count(self._value)
            else:
                return len(table.columns[self._column_name].values_without_nulls())
        else:
            return len(table.rows)


class Min(Aggregation):
    """
    Compute the minimum value in a column. May be applied to columns containing
    :class:`.DateTime` or :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        column = table.columns[self._column_name]

        if (isinstance(column.data_type, Number) or
        isinstance(column.data_type, Date) or
        isinstance(column.data_type, DateTime)):
            return column.data_type

    def validate(self, table):
        column = table.columns[self._column_name]

        if not (isinstance(column.data_type, Number) or
        isinstance(column.data_type, Date) or
        isinstance(column.data_type, DateTime)):
            raise DataTypeError('Min can only be applied to columns containing DateTime orNumber data.')

    def run(self, table):
        column = table.columns[self._column_name]

        return min(column.values_without_nulls())


class Max(Aggregation):
    """
    Compute the maximum value in a column. May be applied to columns containing
    :class:`.DateTime` or :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        column = table.columns[self._column_name]

        if (isinstance(column.data_type, Number) or
        isinstance(column.data_type, Date) or
        isinstance(column.data_type, DateTime)):
            return column.data_type

    def validate(self, table):
        column = table.columns[self._column_name]

        if not (isinstance(column.data_type, Number) or
        isinstance(column.data_type, Date) or
        isinstance(column.data_type, DateTime)):
            raise DataTypeError('Min can only be applied to columns containing DateTime orNumber data.')

    def run(self, table):
        column = table.columns[self._column_name]

        return max(column.values_without_nulls())


class MaxPrecision(Aggregation):
    """
    Compute the most decimal places present for any value in this column.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('MaxPrecision can only be applied to columns containing Number data.')

    def run(self, table):
        column = table.columns[self._column_name]

        return max_precision(column.values_without_nulls())


class Sum(Aggregation):
    """
    Compute the sum of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Sum can only be applied to columns containing Number data.')

    def run(self, table):
        column = table.columns[self._column_name]

        return sum(column.values_without_nulls())


class Mean(Aggregation):
    """
    Compute the mean value of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._sum = Sum(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Mean can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        sum_total = self._sum.run(table)

        return sum_total / len(column.values_without_nulls())


class Median(Aggregation):
    """
    Compute the median value of a column containing :class:`.Number` data.

    This is the 50th percentile. See :class:`Percentiles` for implementation
    details.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._percentiles = Percentiles(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Median can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        percentiles = self._percentiles.run(table)

        return percentiles[50]


class Mode(Aggregation):
    """
    Compute the mode value of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Sum can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls()
        state = defaultdict(int)

        for n in data:
            state[n] += 1

        return max(state.keys(), key=lambda x: state[x])


class IQR(Aggregation):
    """
    Compute the interquartile range of a column containing
    :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._percentiles = Percentiles(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('IQR can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        percentiles = self._percentiles.run(table)

        return percentiles[75] - percentiles[25]


class Variance(Aggregation):
    """
    Compute the sample variance of a column containing
    :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._mean = Mean(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Variance can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls()
        mean = self._mean.run(table)

        return sum((n - mean) ** 2 for n in data) / (len(data) - 1)


class PopulationVariance(Variance):
    """
    Compute the population variance of a column containing
    :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._mean = Mean(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('PopulationVariance can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls()
        mean = self._mean.run(table)

        return sum((n - mean) ** 2 for n in data) / len(data)


class StDev(Aggregation):
    """
    Compute the sample standard of deviation of a column containing
    :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._variance = Variance(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('StDev can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        return self._variance.run(table).sqrt()


class PopulationStDev(StDev):
    """
    Compute the population standard of deviation of a column containing
    :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._population_variance = PopulationVariance(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('PopulationStDev can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        return self._population_variance.run(table).sqrt()


class MAD(Aggregation):
    """
    Compute the `median absolute deviation <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
    of a column containing :class:`.Number` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name
        self._median = Median(column_name)

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('MAD can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        column = table.columns[self._column_name]

        data = column.values_without_nulls_sorted()
        m = self._median.run(table)

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
    def __init__(self, column_name):
        self._column_name = column_name

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Percentiles can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        """
        :returns:
            An instance of :class:`Quantiles`.
        """
        column = table.columns[self._column_name]

        data = column.values_without_nulls_sorted()

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
    def __init__(self, column_name):
        self._column_name = column_name

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Quartiles can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        """
        :returns:
            An instance of :class:`Quantiles`.
        """
        percentiles = Percentiles(self._column_name).run(table)

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
    def __init__(self, column_name):
        self._column_name = column_name

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Quintiles can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        """
        :returns:
            An instance of :class:`Quantiles`.
        """
        percentiles = Percentiles(self._column_name).run(table)

        return Quantiles([percentiles[i] for i in range(0, 101, 20)])


class Deciles(Aggregation):
    """
    The deciles of a column based on the 10th, 20th ... 90th percentiles.

    "Zeroth" (min value) and "Tenth" (max value) deciles are included for
    reference and intuitive indexing.

    See :class:`Percentiles` for implementation details.

    This aggregation can not be applied to a :class:`.TableSet`.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Deciles can only be applied to columns containing Number data.')

        has_nulls = HasNulls(self._column_name).run(table)

        if has_nulls:
            warn_null_calculation(self, column)

    def run(self, table):
        """
        :returns:
            An instance of :class:`Quantiles`.
        """
        percentiles = Percentiles(self._column_name).run(table)

        return Quantiles([percentiles[i] for i in range(0, 101, 10)])


class MaxLength(Aggregation):
    """
    Calculates the longest string in a column containing :class:`.Text` data.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Text):
            raise DataTypeError('MaxLength can only be applied to columns containing Text data.')

    def run(self, table):
        """
        :returns:
            :class:`int`.
        """
        column = table.columns[self._column_name]

        return max([len(d) for d in column.values_without_nulls()])
