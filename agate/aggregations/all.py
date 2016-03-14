#!/usr/bin/env python

from agate.aggregations.base import Aggregation
from agate.data_types import Boolean


class All(Aggregation):
    """
    Returns :code:`True` if all values in a column pass a truth test. The truth
    test may be omitted when testing :class:`.Boolean` data.

    :param test:
        A function that takes a value and returns `True` or `False`.
    """
    def __init__(self, column_name, test=None):
        self._column_name = column_name
        self._test = test

    def get_aggregate_data_type(self, table):
        return Boolean()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Boolean) and not self._test:
            raise ValueError('You must supply a test function for columns containing non-Boolean data.')

    def run(self, table):
        """
        :returns:
            :class:`bool`
        """
        column = table.columns[self._column_name]
        data = column.values()

        if isinstance(column.data_type, Boolean):
            return all(data)

        return all(self._test(d) for d in data)
