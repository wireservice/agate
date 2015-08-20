#!/usr/bin/env python

import six

from journalism.columns.base import *

class TextColumn(Column):
    """
    A column containing unicode/string data.
    """
    def max_length(self):
        return max([len(d) for d in self._data_without_nulls()])

class TextColumnSet(ColumnSet):
    """
    See :class:`ColumnSet` and :class:`TextColumn`.
    """
    def __init__(self, *args, **kwargs):
        super(TextColumnSet, self).__init__(*args, **kwargs)

        self.max_length = ColumnMethodProxy(self, 'max_length')

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
