#!/usr/bin/env python

import six

from journalism.columns.base import *
from journalism.columns.number import NumberType

class TextType(ColumnType):
    """
    Column type for :class:`TextColumn`.
    """
    def cast(self, d):
        """
        Cast a single value to :func:`unicode` (:func:`str` in Python 3).

        :param d: A value to cast.
        :returns: :func:`unicode` (:func:`str` in Python 3) or :code:`None`
        """
        if d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in NULL_VALUES:
                return None

        return six.text_type(d)

    def _create_column(self, table, index):
        return TextColumn(table, index)

    def _create_column_set(self, tableset, index):
        return TextColumnSet(tableset, index)

class TextColumn(Column):
    """
    A column containing unicode/string data.
    """
    def __init__(self, *args, **kwargs):
        super(TextColumn, self).__init__(*args, **kwargs)

        self.max_length = MaxLengthOperation(self)

class MaxLengthOperation(ColumnOperation):
    """
    Calculates the longest string in this column.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self):
        return max([len(d) for d in self._column._data_without_nulls()])
