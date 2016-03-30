#!/usr/bin/env python

from decimal import Decimal

from agate.aggregations.base import Aggregation
from agate.data_types import Number, Text
from agate.exceptions import DataTypeError


class MaxLength(Aggregation):
    """
    Find the length of the longest string in a column.

    :param column_name:
        The name of a column containing :class:`.Text` data.
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

        return Decimal(max([len(d) for d in column.values_without_nulls()]))
