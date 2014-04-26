#!/usr/bin/env python

"""
This module contains the Table object.
"""

import copy

from journalism.columns import ColumnMapping, FloatColumn
from journalism.exceptions import UnsupportedOperationError
from journalism.rows import RowSequence

def transpose(data):
    """
    Utility function for transposing a 2D array of data.
    """
    return zip(*data)

class Table(object):
    """
    A group of columns with names.

    TODO: dedup column names
    """
    def __init__(self, rows, column_types=[], column_names=[], cast=False, validate=False):
        """
        Create a table from rows of data.

        TODO: validate column_types are all subclasses of Column.
        """
        if not column_names:
            column_names = [unicode(d) for d in rows.pop(0)]

        self._data = rows
        self._column_types = column_types
        self._column_names = column_names

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

    def _fork(self, new_data, column_types=[], column_names=[]):
        """
        Create a new table using the metadata from this one.
        Used internally by functions like :meth:`sort_by`.
        """
        if not column_types:
            column_types = self._column_types

        if not column_names:
            column_names = self._column_names

        return Table(new_data, column_types, column_names)

    def sort_by(self, column_name, cmp=None, reverse=False):
        """
        Sort this table by the specified column.

        Returns a new :class:`Table`.
        """
        i = self._column_names.index(column_name)

        data = sorted(self._data, cmp=cmp, key=lambda r: r[i], reverse=reverse)

        return self._fork(data)

    def filter(self, func):
        """
        Filter a to only those rows where the row passes a truth test.

        Returns a new :class:`Table`.
        """
        rows = [self._data[i] for i, row in enumerate(self.rows) if func(row)]

        return self._fork(rows)

    def reject(self, func):
        """
        Filter a to only those rows where the row fails a truth test.

        Returns a new :class:`Table`.
        """
        rows = [self._data[i] for i, row in enumerate(self.rows) if not func(row)]

        return self._fork(rows)

    def where(self, column_name, cmp):
        """
        Filter the data to only those rows where the specified column
        passes a truth test.

        Returns a new :class:`Table`.
        """
        i = self._column_names.index(column_name)

        rows = filter(lambda r: cmp(r[i]), self._data)

        return Table(rows, self._column_types, self._column_names)

    def aggregate(self, group_by, operations=[]):
        """
        Aggregate data by a specified group_by column.

        Operations is a dict of column names and operation names.

        Returns a new :class:`Table`.
        """
        i = self._column_names.index(group_by)

        groups = {}

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

            output.append(new_row)
        
        return self._fork(output, column_types, column_names) 

    def compute(self, column_name, column_type, func):
        """
        Compute a new column by passing each row to a function.
        
        Returns a new :class:`Table`.
        """
        rows = copy.deepcopy(self._data)
        column_types = copy.deepcopy(self._column_types) + [column_type]
        column_names = copy.deepcopy(self._column_names) + [column_name]

        for i, row in enumerate(self.rows):
            rows[i] += [func(row)] 
            
        return self._fork(rows, column_types, column_names)

    def percent_change(self, before_column_name, after_column_name, new_column_name):
        """
        A wrapper around :meth:`compute` for quickly computing
        percent change between two columns.
        """
        def calc(row):
            return float(row[after_column_name] - row[before_column_name]) / row[before_column_name] * 100

        return self.compute(new_column_name, FloatColumn, calc) 

