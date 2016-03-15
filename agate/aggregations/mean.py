#!/usr/bin/env python

from agate.aggregations.base import Aggregation
from agate.aggregations.has_nulls import HasNulls
from agate.aggregations.sum import Sum
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.warns import warn_null_calculation


class Mean(Aggregation):
    """
    Calculate the mean of a column.

    :param column_name:
        The name of a column containing :class:`.Number` data.
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
