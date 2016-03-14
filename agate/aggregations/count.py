#!/usr/bin/env python

from agate.aggregations.base import Aggregation
from agate.data_types import Number
from agate.utils import default

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
