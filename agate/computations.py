#!/usr/bin/env python

"""
This module contains the :class:`Computation` class and its subclasses.
Computations allow for row-wise calculation of new data for :class:`.Table`.
For instance, the :class:`PercentChange` subclass takes two column names as
arguments and computes the percentage change between them for each row.

Computations are applied to tables using the :meth:`.Table.compute` method.
For efficiencies sake, this method accepts a sequence of operations, which are
applied simultaneously.

If the basic computations supplied in this module are not suitable to your needs
the :class:`Formula` subclass can be used to apply an arbitrary function to the
data in each row. If this is still not suitable, :class:`Computation` can be
subclassed to fully customize it's behavior.
"""

from decimal import Decimal
import six

from agate.aggregations import HasNulls, Percentiles, Sum
from agate.data_types import Date, DateTime, Number, TimeDelta
from agate.exceptions import DataTypeError
from agate.warns import warn_null_calculation

if six.PY3:
    from functools import cmp_to_key

@six.python_2_unicode_compatible
class Computation(object):  # pragma: no cover
    """
    An operation that takes a table and produces a new column by performing
    some computation on each row. Computations are invoked with
    :class:`.TableSet.compute`.

    When implementing a custom subclass, ensure that the values returned by
    :meth:`run` are of the type specified by :meth:`get_computed_data_type`.
    This can be ensured by using the :meth:`.DataType.cast` method. See
    :class:`Formula` for an example.
    """
    def __str__(self):
        """
        String representation of this column. May be used as a column name in
        generated tables.
        """
        return self.__class__.__name__

    def get_computed_data_type(self, table):
        """
        Returns an instantiated :class:`.DataType` which will be appended to
        the table.
        """
        raise NotImplementedError()

    def validate(self, table):
        """
        Perform any checks necessary to verify this computation can run on the
        provided table without errors. This is called by :meth:`.Table.compute`
        before :meth:`run`.
        """
        pass

    def run(self, table):
        """
        When invoked with a table, returns a sequence of new column values.
        """
        raise NotImplementedError()


class Formula(Computation):
    """
    A simple drop-in computation that can apply any function to rows.

    :param data_type:
        The data type this formula will return.
    :param func:
        The function to be applied to each row. Must return a valid value for
        the specified data type.
    :param cast:
        If ``True``, each return value will be cast to the specified
        ``data_type`` to ensure it is valid. Only specify false if you are
        certain your formula always returns the correct type.
    """
    def __init__(self, data_type, func, cast=True):
        self._data_type = data_type
        self._func = func
        self._cast = cast

    def get_computed_data_type(self, table):
        return self._data_type

    def run(self, table):
        new_column = []

        for row in table.rows:
            v = self._func(row)

            if self._cast:
                v = self._data_type.cast(v)

            new_column.append(v)

        return new_column


class Change(Computation):
    """
    Computes change between two columns.
    """
    def __init__(self, before_column_name, after_column_name):
        self._before_column_name = before_column_name
        self._after_column_name = after_column_name

    def get_computed_data_type(self, table):
        before_column = table.columns[self._before_column_name]

        if isinstance(before_column.data_type, Date):
            return TimeDelta()
        elif isinstance(before_column.data_type, DateTime):
            return TimeDelta()
        elif isinstance(before_column.data_type, TimeDelta):
            return TimeDelta()
        elif isinstance(before_column.data_type, Number):
            return Number()

    def validate(self, table):
        before_column = table.columns[self._before_column_name]
        after_column = table.columns[self._after_column_name]

        for data_type in (Number, Date, DateTime, TimeDelta):
            if isinstance(before_column.data_type, data_type):
                if not isinstance(after_column.data_type, data_type):
                    raise DataTypeError('Specified columns must be of the same type')

                if HasNulls(self._before_column_name).run(table):
                    warn_null_calculation(self, before_column)

                if HasNulls(self._after_column_name).run(table):
                    warn_null_calculation(self, after_column)

                return

        raise DataTypeError('Change before and after columns must both contain data that is one of: Number, Date, DateTime or TimeDelta.')

    def run(self, table):
        new_column = []

        for row in table.rows:
            before = row[self._before_column_name]
            after = row[self._after_column_name]

            if before and after:
                new_column.append(after - before)
            else:
                new_column.append(None)

        return new_column


class Percent(Computation):
    """
    Computes a column's percentage of a total
    """
    def __init__(self, column_name, total=None):
        self._column_name = column_name
        self._total = total

    def get_computed_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]
        if not isinstance(column.data_type, Number):
            raise DataTypeError('Percent column must contain Number data.')
        if self._total is not None and self._total <= 0:
            raise DataTypeError('The total must be a positive number')
        # Throw a warning if there are nulls in there
        if HasNulls(self._column_name).run(table):
            warn_null_calculation(self, column)

    def run(self, table):
        """
        :returns:
            :class:`decimal.Decimal`
        """
        # If the user has provided a total, use that
        if self._total is not None:
            total = self._total
        # Otherwise compute the sum of all the values in that column to
        # act as our denominator
        else:
            total = table.aggregate(Sum(self._column_name))
            # Raise error if sum is less than or equal to zero
            if total <= 0:
                raise DataTypeError('The sum of column values must be a positive number')

        # Create a list new rows
        new_column = []
        # Loop through the existing rows
        for row in table.rows:
            # Pull the value
            value = row[self._column_name]
            if value is None:
                new_column.append(None)
                continue
            # Try to divide it out of the total
            percent = value / total
            # And multiply it by 100
            percent = percent * 100
            # Append the value to the new list
            new_column.append(percent)
        # Pass out the list
        return new_column


class PercentChange(Computation):
    """
    Computes percent change between two columns.
    """
    def __init__(self, before_column_name, after_column_name):
        self._before_column_name = before_column_name
        self._after_column_name = after_column_name

    def get_computed_data_type(self, table):
        return Number()

    def validate(self, table):
        before_column = table.columns[self._before_column_name]
        after_column = table.columns[self._after_column_name]

        if not isinstance(before_column.data_type, Number):
            raise DataTypeError('PercentChange before column must contain Number data.')

        if not isinstance(after_column.data_type, Number):
            raise DataTypeError('PercentChange after column must contain Number data.')

    def run(self, table):
        """
        :returns:
            :class:`decimal.Decimal`
        """
        new_column = []

        for row in table.rows:
            new_column.append((row[self._after_column_name] - row[self._before_column_name]) / row[self._before_column_name] * 100)

        return new_column


class Rank(Computation):
    """
    Computes rank order of the values in a column.

    Uses the "competition" ranking method: if there are four values and the
    middle two are tied, then the output will be `[1, 2, 2, 4]`.

    Null values will always be ranked last.

    :param column_name:
        The name of the column to rank.
    :param comparer:
        An optional comparison function. If not specified ranking will be
        ascending, with nulls ranked last.
    :param reverse:
        Reverse sort order before ranking.
    """
    def __init__(self, column_name, comparer=None, reverse=None):
        self._column_name = column_name
        self._comparer = comparer
        self._reverse = reverse

    def get_computed_data_type(self, table):
        return Number()

    def run(self, table):
        """
        :returns:
            :class:`int`
        """
        column = table.columns[self._column_name]

        if self._comparer:
            if six.PY3:
                data_sorted = sorted(column.values(), key=cmp_to_key(self._comparer))
            else:  # pragma: no cover
                data_sorted = sorted(column.values(), cmp=self._comparer)
        else:
            data_sorted = column.values_sorted()

        if self._reverse:
            data_sorted.reverse()

        ranks = {}
        rank = 0

        for c in data_sorted:
            rank += 1

            if c in ranks:
                continue

            ranks[c] = Decimal(rank)

        new_column = []

        for row in table.rows:
            new_column.append(ranks[row[self._column_name]])

        return new_column


class PercentileRank(Rank):
    """
    Assign each value in a column to the percentile into which it falls.

    See :class:`.Percentiles` for implementation details.
    """
    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('PercentileRank column must contain Number data.')

    def run(self, table):
        """
        :returns:
            :class:`int`
        """
        percentiles = Percentiles(self._column_name).run(table)

        new_column = []

        for row in table.rows:
            new_column.append(percentiles.locate(row[self._column_name]))

        return new_column
