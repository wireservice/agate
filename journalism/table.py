#!/usr/bin/env python

"""
This module contains the Table object.
"""

from decimal import Decimal

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

from journalism.columns import ColumnMapping, NumberColumn
from journalism.exceptions import UnsupportedOperationError
from journalism.rows import RowSequence, Row

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
    """
    def __init__(self, rows, column_types, column_names, _forked=False):
        """
        Create a table from rows of data.

        Rows is a 2D sequence of any sequences: tuples, lists, etc.
        """
        self._column_types = tuple(column_types)
        self._column_names = tuple(column_names)
        self._cached_columns = {}
        self._cached_rows = {}

        self.columns = ColumnMapping(self)
        self.rows = RowSequence(self)

        cast_data = []

        cast_funcs = [c._get_cast_func() for c in self.columns]

        for row in rows:
            # Forked tables can share data (because they are immutable)
            # but original data should be buffered so it can't be changed
            if isinstance(row, Row):
                cast_data.append(row)

                continue

            cast_data.append(tuple(cast_funcs[i](d) for i, d in enumerate(row)))
        
        self._data = tuple(cast_data) 

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

    def outliers(self, column_name, deviations=3, reject=False):
        """
        A wrapper around :meth:`where` that filters the dataset to
        rows where the value of the column are more than some number
        of standard deviations from the mean.

        If :code:`reject` is False than this method will return
        everything *except* the outliers.

        NB: This method makes no attempt to validate that the
        distribution of your data is normal.

        NB: There are well-known cases in which this algorithm will
        fail to identify outliers. For a more robust measure see
        :meth:`outliers_mad`.
        """
        mean = self.columns[column_name].mean()
        sd = self.columns[column_name].stdev()

        lower_bound = mean - (sd * deviations)
        upper_bound = mean + (sd * deviations)

        if reject:
            f = lambda row: row[column_name] < lower_bound or row[column_name] > upper_bound
        else:
            f = lambda row: lower_bound <= row[column_name] <= upper_bound

        return self.where(f)

    def outliers_mad(self, column_name, deviations=3, reject=False):
        """
        A wrapper around :meth:`where` that filters the dataset to
        rows where the value of the column are more than some number of
        `median absolute deviations <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
        from the median.

        If :code:`reject` is False than this method will return
        everything *except* the outliers.

        NB: This method makes no attempt to validate that the
        distribution of your data is normal.
        """
        median = self.columns[column_name].median()
        mad = self.columns[column_name].mad()

        lower_bound = median - (mad * deviations)
        upper_bound = median + (mad * deviations)

        if reject:
            f = lambda row: row[column_name] < lower_bound or row[column_name] > upper_bound
        else:
            f = lambda row: lower_bound <= row[column_name] <= upper_bound

        return self.where(f)

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
        and from :code:`table` anywhere that the output of :code:`left_key`
        and :code:`right_key` are equivalent. These may be either column
        names or row functions.

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

    def left_outer_join(self, left_key, table, right_key):
        """
        Performs an "left outer join", combining columns from this table
        and from :code:`table` anywhere that the output of :code:`left_key`
        and :code:`right_key` are equivalent. These may be either column
        names or row functions.

        Where there is no match for :code:`left_key`the left columns will
        be included with the right columns set to :code:`None`.

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
            if l in right:
                for j, r in enumerate(right):
                    if l == r:
                        rows.append(tuple(list(self.rows[i]) + list(table.rows[j])))
            else:
                rows.append(tuple(list(self.rows[i]) + [None] * len(table.columns))) 

        column_types = self._column_types + table._column_types
        column_names = self._column_names + table._column_names

        return self._fork(rows, column_types, column_names)

    def group_by(self, group_by):
        """
        Create one new :class:`Table` for each unique value in the
        :code:`group_by` column and return them as a dict.
        """
        i = self._column_names.index(group_by)

        groups = OrderedDict() 

        for row in self._data:
            group_name = row[i]

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append(row)

        output = {}

        for group, rows in groups.items():
            output[group] = self._fork(rows)

        return output

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
            i = self._column_names.index(op_column)
            column_type = self._column_types[i]

            column_types.append(column_type)
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
        column_types = self._column_types + (column_type,)
        column_names = self._column_names + (column_name,)

        new_rows = []

        for row in self.rows:
            new_rows.append(tuple(row) + (func(row),))

        return self._fork(new_rows, column_types, column_names)

    def percent_change(self, before_column_name, after_column_name, new_column_name):
        """
        A wrapper around :meth:`compute` for quickly computing
        percent change between two columns.

        Returns a new :class:`Table`.
        """
        def calc(row):
            return Decimal(row[after_column_name] - row[before_column_name]) / row[before_column_name] * 100

        return self.compute(new_column_name, NumberColumn, calc) 

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
        
        return self.compute(new_column_name, NumberColumn, lambda row: rank_column.index(func(row)) + 1)

