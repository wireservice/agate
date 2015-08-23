#!/usr/bin/env python

from journalism.columns.operations.base import ColumnOperation

class MinDate(ColumnOperation):
    """
    Compute the earliest date in this column.

    :returns: :class:`datetime.date`.
    """
    def get_aggregate_column_type(self):
        return DateType()

    def __call__(self):
        return min(self._column._data_without_nulls())

class MaxDate(ColumnOperation):
    """
    Compute the latest date in this column.

    :returns: :class:`datetime.date`.
    """
    def get_aggregate_column_type(self):
        return DateType()

    def __call__(self):
        return max(self._column._data_without_nulls())
