#!/usr/bin/env python

from agate.aggregations.base import Aggregation
from agate.data_types import Number
from agate.exceptions import DataTypeError


class Sum(Aggregation):
    """
    Calculate the sum of a column.

    :param column_name:
        The name of a column containing :class:`.Number` data.
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
