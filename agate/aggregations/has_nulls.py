#!/usr/bin/env python

from agate.aggregations.base import Aggregation
from agate.data_types import Boolean


class HasNulls(Aggregation):
    """
    Returns :code:`True` if the column contains null values.
    """
    def __init__(self, column_name):
        self._column_name = column_name

    def get_aggregate_data_type(self, table):
        return Boolean()

    def run(self, table):
        return None in table.columns[self._column_name].values()
