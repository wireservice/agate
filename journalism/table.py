#!/usr/bin/env python

"""
This module contains the Table object.
"""

import copy
from decimal import Decimal

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

import six

from journalism.columns import ColumnMapping, IntColumn, DecimalColumn
from journalism.exceptions import UnsupportedOperationError
from journalism.rows import RowSequence, Row

def transpose(data):
    """
    Utility function for transposing a 2D array of data.
    """
    if six.PY3: #pragma: no cover
        # Run generator
        return tuple(zip(*data))

    return zip(*data)
    
class NullOrder(object):
    """
    Dummy object used for sorting in place of None.

    Sorts as "greater than everything but other nulls."
    """
    def __lt__(self, other):
        return False 

    def __gt__(self, other):
        if other is None:
            return False

        return True

class Table(object):
    """
    A group of columns with names.

    TODO: dedup column names
    """
    def __init__(self, rows, column_types, column_names, cast=False, validate=False, _forked=False):
        """
        Create a table from rows of data.

        Rows is a 2D array of any common iterable: tuple, list, etc.

        TODO: validate column_types are all subclasses of Column.
        """
        # Forked tables can share data (because they are immutable)
        # but original data should be buffered so it can't be changed
        if not _forked:
            self._data = copy.deepcopy(rows)
        else:
            self._data = rows

        self._column_types = tuple(column_types)
        self._column_names = tuple(column_names)
        self._cached_columns = {}
        self._cached_rows = {}

        self.columns = ColumnMapping(self)
        self.rows = RowSequence(self)

        if cast:
            data_columns = []

            for column in self.columns:
                data_columns.append(column._cast())
            
            self._data = transpose(data_columns)

        if validate:
            for column in self.columns:
                column.validate()

    def _get_column(self, i):
        """
        Get a Column of data, caching a copy for next request.
        """
        if i not in self._cached_columns:
            column_type = self._column_types[i]

            self._cached_columns[i] = column_type(self, i)

        return self._cached_columns[i]

    def _get_row(self, i):
        """
        Get a Row of data, caching a copy for the next request.
        """
        if i not in self._cached_rows:
            # If rows are from a fork, they are safe to access directly
            if isinstance(self._data[i], Row):
                self._cached_rows[i] = self._data[i]
            else:
                self._cached_rows[i] = Row(self, i)

        return self._cached_rows[i]

    def _fork(self, rows, column_types=[], column_names=[]):
        """
        Create a new table using the metadata from this one.
        Used internally by functions like :meth:`order_by`.
        """
        if not column_types:
            column_types = self._column_types

        if not column_names:
            column_names = self._column_names

        return Table(rows, column_types, column_names, _forked=True)

    def get_column_types(self):
        """
        Get an ordered list of this table's column types.
        """
        return self._column_types

    def get_column_names(self):
        """
        Get an ordered list of this table's column names.
        """
        return self._column_names

    def select(self, column_names):
        """
        Reduce this table to only the specified columns.

        Returns a new :class:`Table`.
        """
        column_indices = tuple(self._column_names.index(n) for n in column_names)
        column_types = tuple(self._column_types[i] for i in column_indices)

        new_rows = []

        for row in self.rows:
            new_rows.append(tuple(row[i] for i in column_indices))

        return self._fork(new_rows, column_types, column_names)

    def where(self, test):
        """
        Filter a to only those rows where the row passes a truth test.

        Returns a new :class:`Table`.
        """
        rows = [row for row in self.rows if test(row)]

        return self._fork(rows)

    def order_by(self, key, reverse=False):
        """
        Sort this table by the :code:`key`. This can be either a
        column_name or callable that returns a value to sort by.

        Returns a new :class:`Table`.
        """
        key_is_row_function = hasattr(key, '__call__')

        def null_handler(row):
            if key_is_row_function:
                k = key(row)
            else:
                k = row[key]

            if k is None:
                return NullOrder() 

            return k

        rows = sorted(self.rows, key=null_handler, reverse=reverse)

        return self._fork(rows)

    def limit(self, start_or_stop=None, stop=None, step=None):
        """
        Filter data to a subset of all rows. If only one argument is specified,
        that many rows will be returned. Otherwise, the arguments function as
        :code:`start`, :code:`stop` and :code:`step`, just like Python's
        builtin :func:`slice`.

        Returns a new :class:`Table`.
        """
        if stop or step:
            return self._fork(self.rows[slice(start_or_stop, stop, step)])
        
        return self._fork(self.rows[:start_or_stop])

    def distinct(self, key=None):
        """
        Filter data to only rows that are unique. Uniqueness is determined
        by the value of :code:`key`. If it is a column name, that column
        will be used to determine uniqueness. If it is a callable, it
        will be passed each row and the resulting values will be used to
        determine uniqueness. If it :code:`None`, the entire row will
        be used to verify uniqueness.

        Returns a new :class:`Table`.
        """
        key_is_row_function = hasattr(key, '__call__')

        uniques = []
        rows = []

        for row in self.rows:
            if key_is_row_function:
                k = key(row)
            elif key is None:
                k = tuple(row)
            else:
                k = row[key]

            if k not in uniques:
                uniques.append(k)
                rows.append(row)

        return self._fork(rows)

    def inner_join(self, left_key, table, right_key):
        """
        Performs an "inner join", combining columns from this table
        and from :code:`table` anywhere that the output of :code:`left_func`
        and :code:`right_func` are equivalent.

        Returns a new :class:`Table`.
        """
        left_key_is_row_function = hasattr(left_key, '__call__')
        right_key_is_row_function = hasattr(right_key, '__call__')

        left = []
        right = []

        if left_key_is_row_function:
            left = [left_key(row) for row in self.rows]
        else:
            c = self._column_names.index(left_key)
            left = self._get_column(c)

        if right_key_is_row_function:
            right = [right_key(row) for row in table.rows]
        else:
            c = table._column_names.index(right_key)
            right = table._get_column(c)

        rows = []

        for i, l in enumerate(left):
            for j, r in enumerate(right):
                if l == r:
                    rows.append(tuple(self.rows[i]) + tuple(table.rows[j]))

        column_types = self._column_types + table._column_types
        column_names = self._column_names + table._column_names

        return self._fork(rows, column_types, column_names)

    def left_outer_join(self, left_func, table, right_func):
        """
        Performs a "left outer join", including all columns from this table
        and any from :code:`table` where the output of :code:`left_func`
        and :code:`right_func` are equivalent.

        Returns a new :class:`Table`.
        """
        left = []
        right = []

        for row in self.rows:
            left.append(left_func(row))

        for row in table.rows:
            right.append(right_func(row))

        rows = []

        for i, l in enumerate(left):
            if l in right:
                for j, r in enumerate(right):
                    if l == r:
                        rows.append(tuple(list(self.rows[i]) + list(table.rows[j])))
            else:
                rows.append(tuple(list(self.rows[i]) + [None] * len(table.columns))) 

        column_types = self._column_types + table._column_types
        column_names = self._column_names + table._column_names

        return self._fork(rows, column_types, column_names)

    def aggregate(self, group_by, operations=[]):
        """
        Aggregate data by a specified group_by column.

        Operations is a dict of column names and operation names.

        Returns a new :class:`Table`.
        """
        i = self._column_names.index(group_by)

        groups = OrderedDict() 

        for row in self._data:
            group_name = row[i]

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append(row)

        output = []

        column_types = [self._column_types[i]]
        column_names = [group_by]

        for op_column in [op[0] for op in operations]:
            column_types.append(self._column_names.index(op_column))
            column_names.append(op_column)

        for name, group_rows in groups.items():
            group_table = Table(group_rows, self._column_types, self._column_names) 
            new_row = [name]

            for op_column, operation in operations:
                c = group_table.columns[op_column]
                
                try:
                    op = getattr(c, operation)
                except AttributeError:
                    raise UnsupportedOperationError(operation, c)

                new_row.append(op())

            output.append(tuple(new_row))
        
        return self._fork(output, column_types, column_names) 

    def compute(self, column_name, column_type, func):
        """
        Compute a new column by passing each row to a function.
        
        Returns a new :class:`Table`.
        """
        # Ensure we have raw data, not Row instances
        rows = [list(row) for row in self._data]

        column_types = list(copy.copy(self._column_types)) + [column_type]
        column_names = list(copy.copy(self._column_names)) + [column_name]

        for i, row in enumerate(self.rows):
            rows[i] = tuple(rows[i] + [func(row)]) 

        return self._fork(rows, column_types, column_names)

    def percent_change(self, before_column_name, after_column_name, new_column_name):
        """
        A wrapper around :meth:`compute` for quickly computing
        percent change between two columns.

        Returns a new :class:`Table`.
        """
        def calc(row):
            return Decimal(row[after_column_name] - row[before_column_name]) / row[before_column_name] * 100

        return self.compute(new_column_name, DecimalColumn, calc) 

    def rank(self, func, new_column_name):
        """
        Creates a new column that is the rank order of the values
        returned by the row function.

        Returns a new :class:`Table`.
        """
        def null_handler(k):
            if k is None:
                return NullOrder() 

            return k

        func_column = [func(row) for row in self.rows]
        rank_column = sorted(func_column, key=null_handler)
        
        return self.compute(new_column_name, IntColumn, lambda row: rank_column.index(func(row)) + 1)

