#!/usr/bin/env python

"""
This module contains the :class:`TableSet` class for working with sets of
related tables such as are created when using :meth:`.Table.group_by`.
"""

from collections import Mapping
from copy import copy

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

from journalism.aggregators import Aggregation
from journalism.column_types import TextType, NumberType
from journalism.exceptions import ColumnDoesNotExistError
from journalism.rows import RowSequence

class TableMethodProxy(object):
    """
    A proxy for :class:`TableSet` methods that converts them to individual
    calls on each :class:`.Table` in the set.
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
    """
    def __init__(self, group):
        self._first_table = list(group.values())[0]
        self._column_types = self._first_table.get_column_types()
        self._column_names = self._first_table.get_column_names()

        for name, table in group.items():
            if table._column_types != self._column_types:
                raise ValueError('Table %i has different column types from the initial table.' % i)

            if table._column_names != self._column_names:
                raise ValueError('Table %i has different column names from the initial table.' % i)

        self._tables = copy(group)

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

    def aggregate(self, aggregations):
        """
        Aggregate data from the tables in this set by performing some
        set of column operations on the groups and coalescing the results into
        a new :class:`.Table`.

        :class:`group` and :class:`count` columns will always be included as at
        the beginning of the output table, before the aggregated columns.

        :code:`aggregations` must be a list of tuples, where each has three
        parts: a :code:`column_name`, a :class:`.Aggregation` instance and a
        :code:`new_column_name`.

        :param aggregations: An list of triples in the format
            :code:`(column_name, aggregator, new_column_name)`.
        :returns: A new :class:`.Table`.
        """
        output = []

        column_types = [TextType(), NumberType()]
        column_names = ['group', 'count']

        for column_name, aggregator, new_column_name in aggregations:
            c = self._first_table.columns[column_name]

            column_types.append(aggregator.get_aggregate_column_type(c))
            column_names.append(new_column_name)

        for name, table in self._tables.items():
            new_row = [name, len(table.rows)]

            for column_name, aggregator, new_column_name in aggregations:
                c = table.columns[column_name]

                new_row.append(c.aggregate(aggregator))

            output.append(tuple(new_row))

        return self._first_table._fork(output, column_types, column_names)
