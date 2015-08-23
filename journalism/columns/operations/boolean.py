#!/usr/bin/env python

from journalism.columns.operations.base import ColumnOperation

class AnyBoolean(ColumnOperation):
    """
    Returns :code:`True` if any value is :code:`True`.
    """
    def get_aggregate_column_type(self):
        return BooleanType()

    def __call__(self):
        return any(self._column._data())

class AllBoolean(ColumnOperation):
    """
    Returns :code:`True` if all values are :code:`True`.
    """
    def get_aggregate_column_type(self):
        return BooleanType()

    def __call__(self):
        return all(self._column._data())
