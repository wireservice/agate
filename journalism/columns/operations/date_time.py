#!/usr/bin/env python

from journalism.columns.operations.base import ColumnOperation

class MinDateTime(ColumnOperation):
    """
    Compute the earliest datetime in this column.

    :returns: :class:`datetime.datetime`.
    """
    def get_aggregate_column_type(self):
        return DateTimeType()

    def __call__(self):
        return min(self._column._data_without_nulls())

class MaxDateTime(ColumnOperation):
    """
    Compute the latest datetime in this column.

    :returns: :class:`datetime.datetime`.
    """
    def get_aggregate_column_type(self):
        return DateTimeType()

    def __call__(self):
        return max(self._column._data_without_nulls())
