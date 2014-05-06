#!/usr/bin/env python

"""
This module contains the Table object.
"""
try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

from journalism.columns import ColumnMapping, NumberType 
from journalism.exceptions import ColumnDoesNotExistError, UnsupportedOperationError
from journalism.rows import RowSequence, Row

class Table(object):
    """
    A dataset consisting of rows and columns.

    :param rows: The data as a sequence of any sequences: tuples, lists, etc.
    :param column_types: A sequence of instances of:class:`.ColumnType`,
        one per column of data.
    :param column_names: A sequence of strings that are names for the columns.

    :var columns: A :class:`.ColumnMapping` for accessing the columns in this
        table.
    :var rows: A :class:`.RowSequence` for accessing the rows in this table.
    """
    def __init__(self, rows, column_types, column_names):
        len_column_types = len(column_types)
        len_column_names = len(column_names)

        if len_column_types != len_column_names:
            raise ValueError('column_types and column_names must be the same length.')

        if len(set(column_names)) != len_column_names:
            raise ValueError('Duplicate column names are not allowed.')

        self._column_types = tuple(column_types)
        self._column_names = tuple(column_names)
        self._cached_columns = {}
        self._cached_rows = {}

        self.columns = ColumnMapping(self)
        self.rows = RowSequence(self)

        cast_data = []

        cast_funcs = [c.cast for c in self._column_types]

        for i, row in enumerate(rows):
            if len(row) != len_column_types:
                raise ValueError('Row %i has length %i, but Table only has %i columns.' % (i, len(row), len_column_types))

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

            self._cached_columns[i] = column_type.create_column(self, i)

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

        return Table(rows, column_types, column_names)

    def get_column_types(self):
        """
        Get an ordered list of this table's column types.

        :returns: A :class:`tuple` of :class:`.Column` instances.
        """
        return self._column_types

    def get_column_names(self):
        """
        Get an ordered list of this table's column names.
        
        :returns: A :class:`tuple` of strings.
        """
        return self._column_names

    def select(self, column_names):
        """
        Reduce this table to only the specified columns.

        :param column_names: A sequence of names of columns to include in the new table. 
        :returns: A new :class:`Table`.
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

        :param test: A function that takes a :class:`.Row` and returns
            :code:`True` if it should be included. 
        :type test: :class:`function`
        :returns: A new :class:`Table`.
        """
        rows = [row for row in self.rows if test(row)]

        return self._fork(rows)

    def find(self, test):
        """
        Find the first row that passes a truth test.

        :param test: A function that takes a :class:`.Row` and returns
            :code:`True` if it matches. 
        :type test: :class:`function`
        :returns: A single :class:`.Row` or :code:`None` if not found.
        """
        for row in self.rows:
            if test(row):
                return row

        return None

    def stdev_outliers(self, column_name, deviations=3, reject=False):
        """
        A wrapper around :meth:`where` that filters the dataset to
        rows where the value of the column are more than some number
        of standard deviations from the mean.

        This method makes no attempt to validate that the distribution
        of your data is normal.

        There are well-known cases in which this algorithm will
        fail to identify outliers. For a more robust measure see
        :meth:`mad_outliers`.

        :param column_name: The name of the column to compute outliers on. 
        :param deviations: The number of deviations from the mean a data point
            must be to qualify as an outlier.
        :param reject: If :code:`True` then the new :class:`Table` will contain 
            everything *except* the outliers.
        :returns: A new :class:`Table`.
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

    def mad_outliers(self, column_name, deviations=3, reject=False):
        """
        A wrapper around :meth:`where` that filters the dataset to
        rows where the value of the column are more than some number of
        `median absolute deviations <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
        from the median.

        This method makes no attempt to validate that the distribution
        of your data is normal.

        :param column_name: The name of the column to compute outliers on. 
        :param deviations: The number of deviations from the median a data point
            must be to qualify as an outlier.
        :param reject: If :code:`True` then the new :class:`Table` will contain 
            everything *except* the outliers.
        :returns: A new :class:`Table`.
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

        :param key: Either the name of a column to sort by or a :class:`function`
            that takes a row and returns a value to sort by. 
        :param reverse: If :code:`True` then sort in reverse (typically, 
            descending) order.
        :returns: A new :class:`Table`.
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
        Filter data to a subset of all rows.
        
        See also: Python's :func:`slice`.

        :param start_or_stop: If the only argument, then how many rows to
            include, otherwise, the index of the first row to include. 
        :param stop: The index of the last row to include.
        :param step: The size of the jump between rows to include.
            (*step=2* will return every other row.)
        :returns: A new :class:`Table`.
        """
        if stop or step:
            return self._fork(self.rows[slice(start_or_stop, stop, step)])
        
        return self._fork(self.rows[:start_or_stop])

    def distinct(self, key=None):
        """
        Filter data to only rows that are unique.

        :param key: Either 1) the name of a column to use to identify
            unique rows or 2) a :class:`function` that takes a row and
            returns a value to identify unique rows or 3) :code:`None`,
            in which case the entire row will be checked for uniqueness.
        :returns: A new :class:`Table`.
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
        and :code:`right_key` are equivalent.

        :param left_key: Either the name of a column from the this table
            to join on, or a :class:`function` that takes a row and returns
            a value to join on. 
        :param table: The "right" table to join to.
        :param right_key: Either the name of a column from :code:table`
            to join on, or a :class:`function` that takes a row and returns
            a value to join on. 
        :returns: A new :class:`Table`.
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
        and :code:`right_key` are equivalent.

        Where there is no match for :code:`left_key`the left columns will
        be included with the right columns set to :code:`None`.

        :param left_key: Either the name of a column from the this table
            to join on, or a :class:`function` that takes a row and returns
            a value to join on. 
        :param table: The "right" table to join to.
        :param right_key: Either the name of a column from :code:table`
            to join on, or a :class:`function` that takes a row and returns
            a value to join on. 
        :returns: A new :class:`Table`.
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
        Create a new :class:`Table` for **each** unique value in the
        :code:`group_by` column and return them as a dict.

        :param group_by: The name of a column to group by. 
        :returns: A :class:`dict` where the keys are unique values from
            the :code:`group_by` column and the values are new :class:`Table`
            instances.
        :raises: :exc:`.ColumnDoesNotExistError`
        """
        try:
            i = self._column_names.index(group_by)
        except ValueError:
            raise ColumnDoesNotExistError(group_by)

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

    def aggregate(self, group_by, operations):
        """
        Aggregate data by grouping values together and performing some
        set of column operations on the groups.

        The columns of the output table (except for the :code:`group_by`
        column, will be named :code:`originalname_operation`. For instance
        :code:`salaries_median`.

        A :code:`group_by_count` column will always be added to the output.
        The order of the output columns will be :code:`('group_by', 
        'group_by_count', 'column_one_operation', ...)`.

        :param group_by: The name of a column to group by. 
        :param operations: A :class:`dict: where the keys are column names
            and the values are the names of :class:`.Column` methods, such
            as "sum" or "max_length".
        :returns: A new :class:`Table`.
        :raises: :exc:`.ColumnDoesNotExistError`, :exc:`.UnsupportedOperationError`
        """
        try:
            i = self._column_names.index(group_by)
        except ValueError:
            raise ColumnDoesNotExistError(group_by)

        groups = OrderedDict() 

        for row in self._data:
            group_name = row[i]

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append(row)

        output = []

        column_types = [self._column_types[i], NumberType()]
        column_names = [group_by, '%s_count' % group_by]

        for op_column, operation in operations:
            try:
                j = self._column_names.index(op_column)
            except ValueError:
                raise ColumnDoesNotExistError(op_column)

            column_type = self._column_types[j]

            column_types.append(column_type)
            column_names.append('%s_%s' % (op_column, operation))

        for name, group_rows in groups.items():
            group_table = Table(group_rows, self._column_types, self._column_names) 
            new_row = [name, len(group_table.rows)]

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
        
        :param column_name: A name of the new column. 
        :param column_type: An instance of :class:`.ColumnType`.
        :param func: A :class:`function` that will be passed a :class:`.Row`
            and should return the computed value for the new column.
        :returns: A new :class:`Table`.
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

        :param before_column_name: The name of the column containing the
            *before* values. 
        :param after_column_name: The name of the column containing the
            *after* values.
        :param new_column_name: The name of the resulting column.
        :returns: A new :class:`Table`.
        """
        def calc(row):
            return (row[after_column_name] - row[before_column_name]) / row[before_column_name] * 100

        return self.compute(new_column_name, NumberType(), calc) 

    def rank(self, key, new_column_name):
        """
        Creates a new column that is the rank order of the values
        returned by the row function.

        :param key:  
        :param after_column_name: The name of the column containing the
            *after* values.
        :param new_column_name: The name of the resulting column.
        :returns: A new :class:`Table`.
        """
        key_is_row_function = hasattr(key, '__call__')

        def null_handler(k):
            if k is None:
                return NullOrder() 

            return k

        if key_is_row_function:
            values = [key(row) for row in self.rows]
            compute_func = lambda row: rank_column.index(key(row)) + 1
        else:
            values = [row[key] for row in self.rows]
            compute_func = lambda row: rank_column.index(row[key]) + 1

        rank_column = sorted(values, key=null_handler)

        return self.compute(new_column_name, NumberType(), compute_func)

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


