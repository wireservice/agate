#!/usr/bin/env python

"""
This module contains re-usable functions for computing new :class:`.Table`
columns.
"""

from journalism.columns import NumberColumn
from journalism.column_types import NumberType
from journalism.exceptions import UnsupportedComputationError
from journalism.utils import NullOrder

class Computer(object): #pragma: no cover
    """
    Base class for computer function classes.
    """
    def get_compute_column_type(self):
        """
        Returns an instantiated :class:`.ColumnType` which will be appended to
        the table.
        """
        raise NotImplementedError()

    def _prepare(self, table):
        """
        Called with the table immediately prior to invoking the computer with
        rows. Can be used to compute column-level statistics for computations.
        By default, this does nothing.
        """
        pass

    def __call__(self, row):
        """
        When invoked with a row, returns the computed new column value.
        """
        raise NotImplementedError()

class Formula(Computer):
    """
    A simple drop-in computer that can apply any function to rows.
    """
    def __init__(self, column_type, func):
        self._column_type = column_type
        self._func = func

    def get_compute_column_type(self):
        return self._column_type

    def __call__(self, row):
        return self._func(row)

class PercentChange(Computer):
    """
    Computes percent change between two columns.
    """
    def __init__(self, before_column, after_column):
        self._before_column = before_column
        self._after_column = after_column

    def get_compute_column_type(self):
        return NumberType()

    def _prepare(self, table):
        before_column = table.columns[self._before_column]

        if not isinstance(before_column, NumberColumn):
            raise UnsupportedComputationError(self, before_column)

        after_column = table.columns[self._before_column]

        if not isinstance(after_column, NumberColumn):
            raise UnsupportedComputationError(self, after_column)

    def __call__(self, row):
        return (row[self._after_column] - row[self._before_column]) / row[self._before_column] * 100

class Rank(Computer):
    """
    Computes rank order of the values in a column.

    NOTE: This rank algorithm is overly-simplistic and currently does not
    handle ties.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_compute_column_type(self):
        return NumberType()

    def _null_handler(self, k):
        if k is None:
            return NullOrder()

        return k

    def _prepare(self, table):
        values = [row[self._column_name] for row in table.rows]
        self._rank_column = sorted(values, key=self._null_handler)

    def __call__(self, row):
        return self._rank_column.index(row[self._column_name]) + 1

class ZScores(Computer):
    """
    Computes the z-score (standard score) of a given column in each row.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_compute_column_type(self):
        return NumberType()

    def _prepare(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column, NumberColumn):
            raise UnsupportedComputationError(self, column)

        self._mean = table.columns[self._column_name].mean()
        self._sd = table.columns[self._column_name].stdev()

    def __call__(self, row):
        return (row[self._column_name] - self._mean) / self._sd
