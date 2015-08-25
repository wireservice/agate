#!/usr/bin/env python

"""
This module contains re-usable functions for computing new :class:`.Table`
columns.
"""

from journalism.aggregators import Mean, StDev
from journalism.columns import NumberColumn
from journalism.column_types import NumberType
from journalism.exceptions import UnsupportedComputationError
from journalism.utils import NullOrder

class Computation(object): #pragma: no cover
    """
    Base class for row-wise computations on :class:`.Table`s.
    """
    def get_computed_column_type(self):
        """
        Returns an instantiated :class:`.ColumnType` which will be appended to
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

    def get_computed_column_type(self):
        return self._column_type

    def run(self, row):
        return self._func(row)

class Change(Computation):
    """
    Computes change between two columns.
    """
    def __init__(self, before_column, after_column):
        self._before_column = before_column
        self._after_column = after_column

    def get_computed_column_type(self):
        return NumberType()

    def prepare(self, table):
        before_column = table.columns[self._before_column]

        if not isinstance(before_column, NumberColumn):
            raise UnsupportedComputationError(self, before_column)

        after_column = table.columns[self._after_column]

        if not isinstance(after_column, NumberColumn):
            raise UnsupportedComputationError(self, after_column)

    def run(self, row):
        return row[self._after_column] - row[self._before_column]

class PercentChange(Change):
    """
    Computes percent change between two columns.
    """
    def run(self, row):
        return (row[self._after_column] - row[self._before_column]) / row[self._before_column] * 100

class ZScores(Computation):
    """
    Computes the z-scores (standard scores) of a given column.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_computed_column_type(self):
        return NumberType()

    def prepare(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column, NumberColumn):
            raise UnsupportedComputationError(self, column)

        self._mean = column.summarize(Mean())
        self._sd = column.summarize(StDev())

    def run(self, row):
        return (row[self._column_name] - self._mean) / self._sd

class Rank(Computation):
    """
    Computes rank order of the values in a column.

    NOTE: This rank algorithm is overly-simplistic and currently does not
    handle ties.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_computed_column_type(self):
        return NumberType()

    def _null_handler(self, k):
        if k is None:
            return NullOrder()

        return k

    def prepare(self, table):
        values = [row[self._column_name] for row in table.rows]
        self._rank_column = sorted(values, key=self._null_handler)

    def run(self, row):
        return self._rank_column.index(row[self._column_name]) + 1
        
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
