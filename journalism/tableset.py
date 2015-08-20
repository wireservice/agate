#!/usr/bin/env python

"""
This module contains the TableGroup object.
"""

from collections import Mapping
from copy import copy

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

from journalism.columns import ColumnMapping
from journalism.rows import RowSequence

class TableSet(Mapping):
    """
    An group of named tables with identical column definitions.

    :param tables: A dictionary of string keys and :class:`Table` values.

    :var columns: A :class:`.ColumnMapping` for accessing the columns in this
        table.
    :var rows: A :class:`.RowSequence` for accessing the rows in this table.
    """
    def __init__(self, group):
        self._column_types = group.values()[0].get_column_types()
        self._column_names = group.values()[0].get_column_names()

        for name, table in group.items():
            if table._column_types != self._column_types:
                raise ValueError('Table %i has different column types from the initial table.' % i)

            if table._column_names != self._column_names:
                raise ValueError('Table %i has different column names from the initial table.' % i)

        self._cached_columns = {}
        self._cached_rows = {}
        self._tables = copy(group)

        self.columns = ColumnMapping(self)
        self.rows = RowSequence(self)

    def __getitem__(self, k):
        return self._tables.__getitem__(k)

    def __iter__(self):
        return self._tables.__iter__()

    def __len__(self):
        return self._tables.__len__()

    def _get_column(self, i):
        """
        Get a Column of data, caching a copy for next request.
        """
        if i not in self._cached_columns:
            column_type = self._column_types[i]

            self._cached_columns[i] = column_type._create_column_set(self, i)

        return self._cached_columns[i]

    def _get_row(self, i):
        """
        Get a Row of data, caching a copy for the next request.
        """
        # TODO: return virtual row
        raise NotImplementedError()

    def get_column_types(self):
        """
        Get an ordered list of this :class:`.TableSet`'s column types.

        :returns: A :class:`tuple` of :class:`.Column` instances.
        """
        return self._column_types

    def get_column_names(self):
        """
        Get an ordered list of this :class:`TableSet`'s column names.

        :returns: A :class:`tuple` of strings.
        """
        return self._column_names

    def select(self, column_names):
        """
        Reduce each table in this set to only the specified columns.

        :param column_names: A sequence of names of columns to include in the new tables.
        :returns: A new :class:`TableSet`.
        """
        groups = OrderedDict()

        for name, table in self._tables.items():
            groups[name] = table.select(column_names)

        return TableSet(groups)

    def where(self, test):
        """
        Filter each table to only those rows where the row passes a truth test.

        :param test: A function that takes a :class:`.Row` and returns
            :code:`True` if it should be included.
        :type test: :class:`function`
        :returns: A new :class:`TableSet`.
        """
        groups = OrderedDict()

        for name, table in self._tables.items():
            groups[name] = table.where(test)

        return TableSet(groups)

    def order_by(self, key, reverse=False):
        """
        Sort each table by the :code:`key`. This can be either a
        column_name or callable that returns a value to sort by.

        :param key: Either the name of a column to sort by or a :class:`function`
            that takes a row and returns a value to sort by.
        :param reverse: If :code:`True` then sort in reverse (typically,
            descending) order.
        :returns: A new :class:`TableSet`.
        """
        groups = OrderedDict()

        for name, table in self._tables.items():
            groups[name] = table.order_by(key, reverse=reverse)

        return TableSet(groups)
