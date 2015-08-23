#!/usr/bin/env python

from journalism.column_types import NumberType
from journalism.columns.operations.base import ColumnOperation

class MaxLength(ColumnOperation):
    """
    Calculates the longest string in this column.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self):
        return max([len(d) for d in self._column._data_without_nulls()])
