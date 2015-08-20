#!/usr/bin/env python

"""
This module contains the TableSet object.
"""

from collections import Mapping
from copy import copy

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

from journalism.columns import ColumnMapping
from journalism.rows import RowSequence

class TableMethodProxy(object):
    """
    A proxy for :class:`TableSet` methods that converts them to individual
    calls on each :class:`Table` in the set.
    """
    def __init__(self, tableset, method_name):
        self.tableset = tableset
        self.method_name = method_name

    def __call__(self, *args, **kwargs):
        groups = OrderedDict()

        for name, table in self.tableset._tables.items():
            groups[name] = getattr(table, self.method_name)(*args, **kwargs)

        return TableSet(groups)

class TableSet(Mapping):
    """
    An group of named tables with identical column definitions. Supports
    (almost) all the same operations as :class:`.Table`. When executed on a
    :class:`TableSet`, any operation that would have returned a new
    :class:`.Table` instead returns a new :class:`TableSet`. Any operation
    that would have returned a single value instead returns a dictionary of
    values.

    :param tables: A dictionary of string keys and :class:`Table` values.

    :var columns: A :class:`.ColumnMapping` for accessing the
        :class:`.ColumnSet`s in this table.
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

        self.select = TableMethodProxy(self, 'select')
        self.where = TableMethodProxy(self, 'where')
        self.find = TableMethodProxy(self, 'find')
        self.stdev_outliers = TableMethodProxy(self, 'stdev_outliers')
        self.mad_outliers = TableMethodProxy(self, 'mad_outliers')
        self.pearson_correlation = TableMethodProxy(self, 'pearson_correlation')
        self.order_by = TableMethodProxy(self, 'order_by')
        self.limit = TableMethodProxy(self, 'limit')
        self.distinct = TableMethodProxy(self, 'distinct')
        self.inner_join = TableMethodProxy(self, 'inner_join')
        self.left_outer_join = TableMethodProxy(self, 'left_outer_join')
        # self.group_by = TableMethodProxy(self, 'group_by')
        self.aggregate = TableMethodProxy(self, 'aggregate')
        self.compute = TableMethodProxy(self, 'compute')
        self.percent_change = TableMethodProxy(self, 'percent_change')
        self.rank = TableMethodProxy(self, 'rank')
        self.z_scores = TableMethodProxy(self, 'z_scores')

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
