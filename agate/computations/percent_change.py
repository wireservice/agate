#!/usr/bin/env python

from agate.computations.base import Computation

from agate.data_types import Number
from agate.exceptions import DataTypeError


class PercentChange(Computation):
    """
    Calculate the percent difference between two columns.

    :param before_column_name:
        The name of a column containing the "before" :class:`.Number` values.
    :param after_column_name:
        The name of a column containing the "after" :class:`.Number` values.
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
