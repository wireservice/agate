#!/usr/bin/env python

from agate.aggregations.base import Aggregation


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
