#!/usr/bin/env python

"""
This module contains the Table object.
"""

import copy
from decimal import Decimal

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import six

from journalism.columns import ColumnMapping, DecimalColumn
from journalism.exceptions import UnsupportedOperationError
from journalism.rows import RowSequence, Row

def transpose(data):
    """
    Utility function for transposing a 2D array of data.
    """
    if six.PY3:
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

    def where(self, func):
        """
        Filter a to only those rows where the row passes a truth test.

        Returns a new :class:`Table`.
        """
        rows = [row for row in self.rows if func(row)]

        return self._fork(rows)

    def order_by(self, func, reverse=False):
        """
        Sort this table by the key returned from the row function.

        See :func:`sorted` for more details.

        Returns a new :class:`Table`.
        """
        def null_handler(row):
            k = func(row)

            if k is None:
                return NullOrder() 

            return k

        data = sorted(self.rows, key=null_handler, reverse=reverse)

        return self._fork(data)

    def limit(self, start_or_stop=None, stop=None, step=None):
        """
        Filter data to a subset of all rows.If only one argument is specified,
        that many rows will be returned. Otherwise, the arguments function as
        `start`, `stop` and `step`, just like Python's builtin :func:`slice`.
        """
        if stop or step:
            return self._fork(self.rows[slice(start_or_stop, stop, step)])
        
        return self._fork(self.rows[:start_or_stop])

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
        """
        def calc(row):
            return Decimal(row[after_column_name] - row[before_column_name]) / row[before_column_name] * 100

        return self.compute(new_column_name, DecimalColumn, calc) 

