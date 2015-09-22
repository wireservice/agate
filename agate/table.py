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

from babel.numbers import format_decimal
import six

from agate.aggregations import *
from agate.columns import *
from agate.data_types import *
from agate.computations import *
from agate.exceptions import *
from agate.rows import *
from agate.tableset import *
from agate.utils import *

class Table(Patchable):
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

        self._columns = ColumnMapping(self)
        self._rows = RowSequence(self)

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

            self._cached_columns[i] = Column(column_type, self, i)

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

        :param path: Filepath or file-like object from which to read CSV data.
        :param column_info: A sequence of pairs of column names and types. The latter
            must be instances of :class:`.DataType`. Or, an instance of
            :class:`.TypeTester` to infer types.
        :param header: If `True`, the first row of the CSV is assumed to contains
            headers and will be skipped.
        """
        use_inference = isinstance(column_info, TypeTester)

        if use_inference and not header:
            raise ValueError('Can not apply TypeTester to a CSV without headers.')

        if hasattr(path, 'read'):
            rows = list(csv.reader(path, **kwargs))
        else:
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

        :param path: Filepath or file-like object to write to.
        """
        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        try:
            if hasattr(path, 'write'):
                f = path
            else:
                f = open(path, 'w')

            writer = csv.writer(f, **kwargs)

            writer.writerow(self._column_names)

            for row in self._data:
                writer.writerow(row)
        finally:
            f.close()

    @property
    def column_types(self):
        """
        Get an ordered list of this table's column types.

        :returns: A :class:`tuple` of :class:`.Column` instances.
        """
        return self._column_types

    @property
    def column_names(self):
        """
        Get an ordered list of this table's column names.

        :returns: A :class:`tuple` of strings.
        """
        return self._column_names

    @property
    def rows(self):
        """
        Get this tables :class:`.RowSequence`.
        """
        return self._rows

    @property
    def columns(self):
        """
        Get this tables :class:`.ColumnMapping`.
        """
        return self._columns

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

        if x.aggregate(HasNulls()) or y.aggregate(HasNulls()):
            raise NullCalculationError

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

    def join(self, right_table, left_key, right_key=None, inner=False):
        """
        Performs the equivalent of SQL's "left outer join", combining columns
        from this table and from :code:`right_table` anywhere that the output of
        :code:`left_key` and :code:`right_key` are equivalent.

        Where there is no match for :code:`left_key` the left columns will
        be included with the right columns set to :code:`None` unless
        the :code:`inner` argument is specified. (See arguments for more.)

        If :code:`left_key` and :code:`right_key` are column names, only
        the left column will be included in the output table.

        Column names from the right table which also exist in this table will
        be suffixed "2" in the new table.

        :param right_table: The "right" table to join to.
        :param left_key: Either the name of a column from the this table
            to join on, or a :class:`function` that takes a row and returns
            a value to join on.
        :param right_key: Either the name of a column from :code:table`
            to join on, or a :class:`function` that takes a row and returns
            a value to join on. If :code:`None` then :code:`left_key` will be
            used for both.
        :param inner: Perform a SQL-style "inner join" instead of a left outer
            join. Rows which have no match for :code:`left_key` will not be
            included in the output table.
        :returns: A new :class:`Table`.
        """
        left_key_is_row_function = hasattr(left_key, '__call__')

        if right_key is None:
            right_key = left_key

        right_key_is_row_function = hasattr(right_key, '__call__')

        # Get join columns
        left_key_index = None
        right_key_index = None

        if left_key_is_row_function:
            left_column = [left_key(row) for row in self.rows]
        else:
            left_key_index = self._column_names.index(left_key)
            left_column = self._get_column(left_key_index)

        if right_key_is_row_function:
            right_column = [right_key(row) for row in right_table.rows]
        else:
            right_key_index = right_table._column_names.index(right_key)
            right_column = right_table._get_column(right_key_index)

        # Build names and type lists
        column_names = list(self._column_names)
        column_types = list(self._column_types)

        for i, name in enumerate(right_table.column_names):
            if i == right_key_index:
                continue

            if name in self._column_names:
                column_names.append('%s2' % name)
            else:
                column_names.append(name)

            column_types.append(self._column_types[i])

        # Collect new rows
        rows = []

        for i, l in enumerate(left_column):
            if l in right_column:
                for j, r in enumerate(right_column):
                    if l == r:
                        row = list(self.rows[i])

                        for k, v in enumerate(right_table.rows[j]):
                            if k == right_key_index:
                                continue

                            row.append(v)

                        rows.append(row)
            elif not inner:
                row = list(self.rows[i])

                for k, v in enumerate(right_table.column_names):
                    if k == right_key_index:
                        continue

                    row.append(None)

                rows.append(row)

        return self._fork(rows, zip(column_names, column_types))

    @classmethod
    def merge(cls, tables):
        """
        Merge an array of tables with identical columns into a single table.
        Each table must have exactly the same column types. Their column names
        need not be identical. The first table's column names will be the ones
        which are used.

        :param tables: An array of :class:`Table`.
        :returns: A new :class:`Table`.
        """
        column_names = tables[0].column_names
        column_types = tables[0].column_types

        for table in tables[1:]:
            if table.column_types != column_types:
                raise ValueError('Only tables with identical column types may be merged.')

        rows = chain(*[table.rows for table in tables])

        return Table(rows, zip(column_names, column_types))

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
            key_type = key_type or Text()
        else:
            key_name = key_name or key

            try:
                i = self._column_names.index(key)
            except ValueError:
                raise ColumnDoesNotExistError(key)

            key_type = key_type or self._column_types[i]

        groups = OrderedDict()

        for row in self.rows:
            if key_is_row_function:
                group_name = key_type.cast(key(row))
            else:
                group_name = key_type.cast(row[i])

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

        for computation, new_column_name in computations:
            if not isinstance(computation, Computation):
                raise ValueError('The first element in pair must be a Computation instance.')

            column_names.append(new_column_name)
            column_types.append(computation.get_computed_data_type(self))

            computation.prepare(self)

        new_rows = []

        for row in self.rows:
            new_columns = tuple(c.run(row) for c, n in computations)
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

        rows_truncated = max_rows < len(self._data)
        columns_truncated = max_columns < len(self._column_names)

        column_names = list(self._column_names[:max_columns])

        if columns_truncated:
            column_names.append('...')

        widths = [len(n) for n in column_names]
        decimal_places = []
        formatted_data = []

        # Determine correct number of decimal places for each Number column
        for i, c in enumerate(self.columns):
            if i >= max_columns:
                break

            if isinstance(c.data_type, Number):
                max_places = 0

                for j, d in enumerate(c):
                    if j >= max_rows:
                        break

                    if d is None:
                        continue

                    places = d.as_tuple().exponent * -1

                    if places > max_places:
                        max_places = places

                decimal_places.append(max_places)
            else:
                decimal_places.append(None)

        # Format data and display column widths
        for i, row in enumerate(self._data):
            if i >= max_rows:
                break

            formatted_row = []

            for j, v in enumerate(row):
                if j >= max_columns:
                    v = '...'
                elif v is None:
                    v = ''
                elif decimal_places[j] is not None:
                    fraction = '0' * decimal_places[j]
                    fmt = ''.join(['#,##0.', fraction, ';-#,##0.', fraction])
                    v = format_decimal(v, format=fmt)
                else:
                    v = six.text_type(v)

                if len(v) > widths[j]:
                    widths[j] = len(v)

                formatted_row.append(v)

                if j >= max_columns:
                    break

            formatted_data.append(formatted_row)

        def _print_row(formatted_row, type_format=True):
            """
            Helper function that formats individual rows.
            """
            row_output = []

            for j, d in enumerate(formatted_row):
                # Text is left-justified, all other values are right-justified
                if isinstance(self._column_types[j], Text):
                    row_output.append(' %s ' % d.ljust(widths[j]))
                else:
                    row_output.append(' %s ' % d.rjust(widths[j]))

            return '| %s |\n' % ('|'.join(row_output))

        # Dashes span each width with '+' character at intersection of
        # horizontal and vertical dividers.
        divider = '|--' + '-+-'.join('-' * w for w in widths) + '--|\n'

        # Initial divider
        output.write(divider)

        # Headers
        output.write(_print_row(column_names, False))
        output.write(divider)

        # Rows
        for formatted_row in formatted_data:
            output.write(_print_row(formatted_row))

        # Row indicating data was truncated
        if rows_truncated:
            output.write(_print_row(['...' for n in column_names], False))

        # Final divider
        output.write(divider)
