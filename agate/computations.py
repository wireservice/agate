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

from agate.aggregations import Mean, StDev
from agate.columns import *
from agate.data_types import *
from agate.exceptions import UnsupportedComputationError
from agate.utils import NullOrder

class Computation(object): #pragma: no cover
    """
    Base class for row-wise computations on a :class:`.Table`.
    """
    def get_computed_column_type(self, table):
        """
        Returns an instantiated :class:`.DataType` which will be appended to
        the table.
        """
        raise NotImplementedError()

    def prepare(self, table):
        """
        Called with the table immediately prior to invoking the computation with
        rows. Can be used to compute column-level statistics for computations.
        By default, this does nothing.
        """
        pass

    def run(self, row):
        """
        When invoked with a row, returns the computed new column value.
        """
        raise NotImplementedError()

class Formula(Computation):
    """
    A simple drop-in computation that can apply any function to rows.
    """
    def __init__(self, column_type, func):
        self._column_type = column_type
        self._func = func

    def get_computed_column_type(self, table):
        return self._column_type

    def run(self, row):
        return self._func(row)

class Change(Computation):
    """
    Computes change between two columns.
    """
    def __init__(self, before_column_name, after_column_name):
        self._before_column_name = before_column_name
        self._after_column_name = after_column_name

    def _validate(self, table):
        before_column = table.columns[self._before_column_name]
        after_column = table.columns[self._after_column_name]

        for column_type in (NumberColumn, DateTimeColumn, TimeDeltaColumn):
            if isinstance(before_column, column_type):
                if not isinstance(after_column, column_type):
                    raise ValueError('Specified columns must be of the same type')

                if before_column.has_nulls():
                    raise NullCalculationError

                if after_column.has_nulls():
                    raise NullCalculationError

                return (before_column, after_column)

        raise UnsupportedComputationError(self, before_column)

    def get_computed_column_type(self, table):
        before_column, after_column = self._validate(table)

        if isinstance(before_column, DateTimeColumn):
            return TimeDeltaType()
        elif isinstance(before_column, TimeDeltaColumn):
            return TimeDeltaType()
        elif isinstance(before_column, NumberColumn):
            return NumberType()

    def prepare(self, table):
        self._validate(table)

    def run(self, row):
        return row[self._after_column_name] - row[self._before_column_name]

class PercentChange(Computation):
    """
    Computes percent change between two columns.
    """
    def __init__(self, before_column_name, after_column_name):
        self._before_column_name = before_column_name
        self._after_column_name = after_column_name

    def get_computed_column_type(self, table):
        return NumberType()

    def prepare(self, table):
        before_column = table.columns[self._before_column_name]
        after_column = table.columns[self._after_column_name]

        if not isinstance(before_column, NumberColumn):
            raise UnsupportedComputationError(self, before_column)

        if not isinstance(after_column, NumberColumn):
            raise UnsupportedComputationError(self, after_column)

    def run(self, row):
        return (row[self._after_column_name] - row[self._before_column_name]) / row[self._before_column_name] * 100

class ZScores(Computation):
    """
    Computes the z-scores (standard scores) of a given column.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_computed_column_type(self, table):
        return NumberType()

    def prepare(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column, NumberColumn):
            raise UnsupportedComputationError(self, column)

        self._mean = column.aggregate(Mean())
        self._sd = column.aggregate(StDev())

    def run(self, row):
        return (row[self._column_name] - self._mean) / self._sd

class Rank(Computation):
    """
    Computes rank order of the values in a column.

    Uses the "competition" ranking method: if there are four values and the
    middle two are tied, then the output will be :code:`[1, 2, 2, 4]`.

    Null values will always be ranked last.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_computed_column_type(self, table):
        return NumberType()

    def prepare(self, table):
        self._ranks = {}
        rank = 0

        for c in table.columns[self._column_name].get_data_sorted():
            rank += 1

            if c in self._ranks:
                continue

            self._ranks[c] = rank

    def run(self, row):
         return self._ranks[row[self._column_name]]

class PercentileRank(Rank):
    """
    Assign each value in a column to the percentile into which it falls.

    See :class:`.Percentiles` for implementation details.
    """
    def prepare(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column, NumberColumn):
            raise UnsupportedComputationError(self, column)

        self._percentiles = column.percentiles()

    def run(self, row):
        return self._percentiles.locate(row[self._column_name])
