#!/usr/bin/env python

"""
This module contains the :class:`Table` object, which is the central data
structure in :code:`agate`. Tables are created by supplying row data, column
names and subclasses of :class:`.DataType` to the constructor. Once
instantiated tables are **immutable**. This concept is central to agate. The
table of the data may not be accessed or modified directly.

Various methods on the :class:`Table` simulate "SQL-like" operations. For
example, the :meth:`Table.select` method reduces the table to only the
specified columns. The :meth:`Table.where` method reduces the table to only
those rows that pass a truth test. And the :meth:`Table.order_by` method sorts
the rows in the table. In all of these cases the output is new :class:`Table`
and the existing table remains unmodified.

Tables are not themselves iterable, but the columns of the table can be
accessed via :attr:`Table.columns` and the rows via :attr:`Table.rows`.
"""

from copy import copy
from itertools import chain
import sys

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

try:
    import csvkit as csv
except ImportError: #pragma: no cover
    import csv

import six

from agate.aggregations import Sum, Mean, Median, StDev, MAD
from agate.columns.base import ColumnMapping
from agate.data_types import TypeTester
from agate.computations import Computation
from agate.exceptions import ColumnDoesNotExistError, RowDoesNotExistError
from agate.rows import RowSequence, Row
from agate.tableset import TableSet
from agate.utils import NullOrder, memoize

class Table(object):
    """
    A dataset consisting of rows and columns.

    :param rows: The data as a sequence of any sequences: tuples, lists, etc.
    :param column_info: A sequence of pairs of column names and types. The latter
        must be instances of :class:`.DataType`.

    :attr columns: A :class:`.ColumnMapping` for accessing the columns in this
        table.
    :attr rows: A :class:`.RowSequence` for accessing the rows in this table.
    """
    def __init__(self, rows, column_info):
        column_names, column_types = zip(*column_info)

        len_column_names = len(column_names)

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
            if len(row) != len_column_names:
                raise ValueError('Row %i has length %i, but Table only has %i columns.' % (i, len(row), len_column_names))

            # Forked tables can share data (because they are immutable)
            # but original data should be buffered so it can't be changed
            if isinstance(row, Row):
                cast_data.append(row)

                continue

            cast_data.append(tuple(cast_funcs[i](d) for i, d in enumerate(row)))

        self._data = tuple(cast_data)

    def _get_column(self, i):
        """
        Get a :class:`.Column` of data, caching a copy for next request.
        """
        if i not in self._cached_columns:
            column_type = self._column_types[i]

            self._cached_columns[i] = column_type.create_column(self, i)

        return self._cached_columns[i]

    def _get_row(self, i):
        """
        Get a :class:`.Row` of data, caching a copy for the next request.
        """
        if i not in self._cached_rows:
            # If rows are from a fork, they are safe to access directly
            if isinstance(self._data[i], Row):
                self._cached_rows[i] = self._data[i]
            else:
                self._cached_rows[i] = Row(self, i)

        return self._cached_rows[i]

    def _get_row_count(self):
        return len(self._data)

    def _fork(self, rows, column_info=None):
        """
        Create a new table using the metadata from this one.
        Used internally by functions like :meth:`order_by`.
        """
        if not column_info:
            column_info = zip(self._column_names, self._column_types)

        return Table(rows, column_info)

    @classmethod
    def from_csv(cls, path, column_info, header=True, **kwargs):
        """
        Create a new table for a CSV. This method will use csvkit if it is
        available, otherwise it will use Python's builtin csv module.

        ``kwargs`` will be passed through to :meth:`csv.reader`.

        If you are using Python 2 and not using csvkit, this method is not
        unicode-safe.

        :param path: Path to the CSV file to read from.
        :param column_info: A sequence of pairs of column names and types. The latter
            must be instances of :class:`.DataType`. Or, an instance of
            :class:`.TypeTester` to infer types.
        :param header: If `True`, the first row of the CSV is assumed to contains
            headers and will be skipped.
        """
        use_inference = isinstance(column_info, TypeTester)

        if use_inference and not header:
            raise ValueError('Can not apply TypeTester to a CSV without headers.')

        with open(path) as f:
            rows = list(csv.reader(f, **kwargs))

        if header:
            column_names = rows.pop(0)

        if use_inference:
            column_info = column_info.run(rows, column_names)
        else:
            if len(column_names) != len(column_info):
                # TKTK Better Error
                raise ValueError('CSV contains more columns than were specified.')

        return Table(rows, column_info)

    def to_csv(self, path, **kwargs):
        """
        Write this table to a CSV. This method will use csvkit if it is
        available, otherwise it will use Python's builtin csv module.

        ``kwargs`` will be passed through to :meth:`csv.writer`.

        If you are using Python 2 and not using csvkit, this method is not
        unicode-safe.

        :param path: Path to the CSV file to read from.
        """
        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        with open(path, 'w') as f:
            writer = csv.writer(f, **kwargs)

            writer.writerow(self._column_names)

            for row in self._data:
                writer.writerow(row)

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

        return self._fork(new_rows, zip(column_names, column_types))

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
        mean = self.columns[column_name].aggregate(Mean())
        sd = self.columns[column_name].aggregate(StDev())

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
        median = self.columns[column_name].aggregate(Median())
        mad = self.columns[column_name].aggregate(MAD())

        lower_bound = median - (mad * deviations)
        upper_bound = median + (mad * deviations)

        if reject:
            f = lambda row: row[column_name] < lower_bound or row[column_name] > upper_bound
        else:
            f = lambda row: lower_bound <= row[column_name] <= upper_bound

        return self.where(f)

    def pearson_correlation(self, column_one, column_two):
        """
        Calculates the `Pearson correlation coefficient <http://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient>`_
        for :code:`column_one` and :code:`column_two`.

        Returns a number between -1 and 1 with 0 implying no correlation. A correlation close to 1 implies a high positive correlation i.e. as x increases so does y. A correlation close to -1 implies a high negative correlation i.e. as x increases, y decreases.

        Note: this implementation is borrowed from the MIT licensed `latimes-calculate <https://github.com/datadesk/latimes-calculate/blob/master/calculate/pearson.py>`_. Thanks, LAT!

        :param column_one: The name of a column.
        :param column_two: The name of a column.
        :returns: :class:`decimal.Decimal`.
        """
        x = self.columns[column_one]
        y = self.columns[column_two]

        if x.has_nulls() or y.has_nulls():
            raise NullComputationError

        n = len(x)

        sum_x = x.aggregate(Sum())
        sum_y = y.aggregate(Sum())

        square = lambda x: pow(x,2)
        sum_x_sq = sum(map(square, x))
        sum_y_sq = sum(map(square, y))

        product_sum = sum((x_val * y_val for x_val, y_val in zip(x, y)))

        pearson_numerator = product_sum - (sum_x * sum_y / n)
        pearson_denominator = ((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n)).sqrt()

        if pearson_denominator == 0:
            return 0

        return pearson_numerator / pearson_denominator

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

        return self._fork(rows, zip(column_names, column_types))

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

        return self._fork(rows, zip(column_names, column_types))

    def group_by(self, key, key_name=None, key_type=None):
        """
        Create a new :class:`Table` for unique value and return them as a
        :class:`.TableSet`. The :code:`key` can be either a column name
        or a function that returns a value to group by.

        Note that when group names will always be coerced to a string,
        regardless of the format of the input column.

        :param key: Either the name of a column from the this table
            to group by, or a :class:`function` that takes a row and returns
            a value to group by.
        :param key_name: A name that describes the grouped properties.
            Defaults to the column name that was grouped on or "group" if
            grouping with a key function. See :class:`.TableSet` for more.
        :param key_type: An instance some subclass of :class:`.DataType`. If
            not provided it will default to a :class`.Text`.
        :returns: A :class:`.TableSet` mapping where the keys are unique
            values from the :code:`key` and the values are new :class:`Table`
            instances containing the grouped rows.
        :raises: :exc:`.ColumnDoesNotExistError`
        """
        key_is_row_function = hasattr(key, '__call__')

        if key_is_row_function:
            key_name = key_name or 'group'
        else:
            key_name = key_name or key

            try:
                i = self._column_names.index(key)
            except ValueError:
                raise ColumnDoesNotExistError(key)

        groups = OrderedDict()

        for row in self.rows:
            if key_is_row_function:
                group_name = six.text_type(key(row))
            else:
                group_name = six.text_type(row[i])

            # print group_name

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append(row)

        output = OrderedDict()

        for group, rows in groups.items():
            output[group] = self._fork(rows)

        return TableSet(output, key_name=key_name, key_type=key_type)

    def compute(self, computations):
        """
        Compute new columns by applying one or more :class:`.Computation` to
        each row.

        :param computations: An iterable of pairs of new column names and
            :class:`.Computation` instances.
        :returns: A new :class:`Table`.
        """
        column_names = list(copy(self._column_names))
        column_types = list(copy(self._column_types))

        for name, computation in computations:
            if not isinstance(computation, Computation):
                raise ValueError('The second element in pair must be a Computation instance.')

            column_names.append(name)
            column_types.append(computation.get_computed_column_type(self))

            computation.prepare(self)

        new_rows = []

        for row in self.rows:
            new_columns = tuple(c.run(row) for n, c in computations)
            new_rows.append(tuple(row) + new_columns)

        return self._fork(new_rows, zip(column_names, column_types))

    def pretty_print(self, max_rows=None, max_columns=None, output=sys.stdout):
        """
        Print a well-formatted preview of this table to the console or any
        other output.

        :param max_rows: The maximum number of rows to display before
            truncating the data.
        :param max_columns: The maximum number of columns to display before
            truncating the data.
        :param output: A file-like object to print to. Defaults to
            :code:`sys.stdout`.
        """
        if max_rows is None:
            max_rows = len(self._data)

        if max_columns is None:
            max_columns = len(self._column_names)

        widths = []
        rows_truncated = False
        columns_truncated = False

        for i, row in enumerate(chain([self._column_names], self._data)):
            if i >= max_rows + 1:
                rows_truncated = True

                break

            for j, v in enumerate(row):
                if j >= max_columns:
                    columns_truncated = True

                    try:
                        widths[j] = 3
                    except IndexError:
                        widths.append(3)

                    break

                v = six.text_type(v)

                try:
                    if len(v) > widths[j]:
                        widths[j] = len(v)
                except IndexError:
                    widths.append(len(v))

        def _format_row(row):
            """
            Helper function that formats individual rows.
            """
            row_output = []

            for j, d in enumerate(row):
                if j >= max_columns:
                    break

                if d is None:
                    d = ''
                row_output.append(' %s ' % six.text_type(d).ljust(widths[j]))

            if columns_truncated:
                row_output.append(' %s ' % six.text_type('...').ljust(widths[j]))

            return '| %s |\n' % ('|'.join(row_output))

        # Dashes span each width with '+' character at intersection of
        # horizontal and vertical dividers.
        divider = '|--' + '-+-'.join('-' * w for w in widths) + '--|\n'

        # Initial divider
        output.write(divider)

        # Rows
        for i, row in enumerate(chain([self._column_names], self._data)):
            if i >= max_rows + 1:
                break

            output.write(_format_row(row))

            # Divider under headers
            if (i == 0):
                output.write(divider)

        # Row indicating data was truncated
        if rows_truncated:
            output.write(_format_row(['...' for n in self._column_names]))

        # Final divider
        output.write(divider)
