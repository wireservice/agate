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
    from cdecimal import Decimal, ROUND_FLOOR
except ImportError: #pragma: no cover
    from decimal import Decimal, ROUND_FLOOR

from babel.numbers import format_decimal

try:
    import csvkit as csv
except ImportError: #pragma: no cover
    import csv

from six.moves import range

from agate.aggregations import Min, Max
from agate.columns import Column, ColumnMapping
from agate.data_types import TypeTester, Text, Number
from agate.computations import Computation
from agate.preview import print_table, print_bars
from agate.rows import Row, RowSequence
from agate.utils import NullOrder, Patchable, max_precision, make_number_formatter, round_limits

def allow_tableset_proxy(func):
    """
    Decorator to flag that a given Table method can be proxied as a :class:`TableSet` method.
    """
    func.allow_tableset_proxy = True

    return func

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

    def __repr__(self):
        return u'<agate.Table: columns=%i rows=%i>' % (
            len(self.columns),
            len(self.rows)
        )

    def _get_column(self, i):
        """
        Get a :class:`.Column` of data, caching a copy for next request.
        """
        if i not in self._cached_columns:
            self._cached_columns[i] = Column(self, i)

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

    @property
    def data(self):
        """
        Get the data underlying this table.
        """
        return self._data

    @allow_tableset_proxy
    def select(self, column_names):
        """
        Reduce this table to only the specified columns.

        :param column_names: A sequence of names of columns to include in the new table.
        :returns: A new :class:`Table`.
        """
        column_indices = []
        column_types = []

        for name in column_names:
            column = self.columns[name]
            column_indices.append(column.index)
            column_types.append(column.data_type)

        new_rows = []

        for row in self.rows:
            new_rows.append(tuple(row[i] for i in column_indices))

        return self._fork(new_rows, zip(column_names, column_types))

    @allow_tableset_proxy
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

    @allow_tableset_proxy
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

    @allow_tableset_proxy
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

    @allow_tableset_proxy
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

    @allow_tableset_proxy
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

    @allow_tableset_proxy
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
            left_column = self.columns[left_key]

        if right_key_is_row_function:
            right_column = [right_key(row) for row in right_table.rows]
        else:
            right_column = right_table.columns[right_key]
            right_key_index = right_column.index

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

            column_types.append(right_table._column_types[i])

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

    @allow_tableset_proxy
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
        """
        from agate.tableset import TableSet

        key_is_row_function = hasattr(key, '__call__')

        if key_is_row_function:
            key_name = key_name or 'group'
            key_type = key_type or Text()
        else:
            column = self.columns[key]
            index = column.index

            key_name = key_name or column.name
            key_type = key_type or column.data_type

        groups = OrderedDict()

        for row in self.rows:
            if key_is_row_function:
                group_name = key(row)
            else:
                group_name = row[index]

            group_name = key_type.cast(group_name)

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append(row)

        output = OrderedDict()

        for group, rows in groups.items():
            output[group] = self._fork(rows)

        return TableSet(output, key_name=key_name, key_type=key_type)

    @allow_tableset_proxy
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

    @allow_tableset_proxy
    def counts(self, key, key_name=None, key_type=None):
        """
        Count the number of occurrences of each distinct value in a column.
        Creates a new table with only the value and the count. This is
        effectively equivalent to doing a :meth:`Table.group_by` followed by an
        :meth:`.TableSet.aggregate` with a :class:`.Length` aggregator.

        The resulting table will have two columns. The first will have
        the name and type of the specified :code:`key` column or
        :code:`key_name` and :code:`key_type`, if specified. The second will be
        named :code:`count` and will be of type :class:`.Number`.

        :param key: Either the name of a column from the this table
            to count, or a :class:`function` that takes a row and returns
            a value to count.
        :param key_name: A name that describes the counted properties.
            Defaults to the column name that was counted or "group" if
            counting with a key function.
        :param key_type: An instance some subclass of :class:`.DataType`. If
            not provided it will default to a :class`.Text`.
        """
        key_is_row_function = hasattr(key, '__call__')

        if key_is_row_function:
            key_name = key_name or 'group'
            key_type = key_type or Text()
        else:
            column = self.columns[key]
            index = column.index

            key_name = key_name or column.name
            key_type = key_type or column.data_type

        output = OrderedDict()

        for row in self.rows:
            if key_is_row_function:
                group_name = key(row)
            else:
                group_name = row[index]

            group_name = key_type.cast(group_name)

            if group_name not in output:
                output[group_name] = 0

            output[group_name] += 1

        column_names = [key_name, 'count']
        column_types = [key_type, Number()]

        return Table(output.items(), zip(column_names, column_types))

    @allow_tableset_proxy
    def bins(self, column_name, count=10, start=None, end=None):
        """
        Generates (approximately) evenly sized bins for the values in a column.
        Bins may not be perfectly even if the spread of the data does not divide
        evenly, but all values will always be included in some bin.

        The resulting table will have two columns. The first will have
        the same name as the specified column, but will be type :class:`.Text`.
        The second will be named :code:`count` and will be of type
        :class:`.Number`.

        :param column_name: The name of the column to bin. Must be of type
            :class:`.Number`
        :param count: The number of bins to create. If not specified then each
            value will be counted as its own bin.
        :param start: The minimum value to start the bins at. If not specified the
            minimum value in the column will be used.
        :param end: The maximum value to end the bins at. If not specified the
            maximum value in the column will be used.
        :returns: A new :class:`Table`.
        """
        column = self.columns[column_name]

        if start is None or end is None:
            start, end = round_limits(
                column.aggregate(Min()),
                column.aggregate(Max())
            )
        else:
            start = Decimal(start)
            end = Decimal(end)

        spread = abs(end - start)
        size = spread / count

        breaks = [start]

        for i in range(1, count + 1):
            top = start + (size * i)

            breaks.append(top)

        decimal_places = max_precision(breaks)
        break_formatter = make_number_formatter(decimal_places)

        def name_bin(i, j, first_exclusive=True, last_exclusive=False):
            inclusive = format_decimal(i, format=break_formatter)
            exclusive = format_decimal(j, format=break_formatter)

            output = u'[' if first_exclusive else u'('
            output += u'%s - %s' % (inclusive, exclusive)
            output += u']' if last_exclusive else u')'

            return output

        bins = OrderedDict()

        for i in range(1, len(breaks)):
            last_exclusive = (i == len(breaks) - 1)
            name = name_bin(breaks[i - 1], breaks[i], last_exclusive=last_exclusive)

            bins[name] = Decimal('0')

        for row in self.rows:
            value = row[column_name]

            if value is None:
                try:
                    bins[None] += 1
                except KeyError:
                    bins[None] = Decimal('1')

                continue

            i = 1

            try:
                while value >= breaks[i]:
                    i += 1
            except IndexError:
                i -= 1

            last_exclusive = (i == len(breaks) - 1)
            name = name_bin(breaks[i - 1], breaks[i], last_exclusive=last_exclusive)

            bins[name] += 1

        return Table(bins.items(), [(column_name, Text()), ('count', Number())])

    def print_table(self, max_rows=None, max_columns=None, output=sys.stdout):
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
        print_table(self, max_rows, max_columns, output)

    def print_bars(self, label_column_name, value_column_name, domain=None, width=120, output=sys.stdout):
        """
        Print a text-based bar chart of the columns names `label_column_name`
        and `value_column_name`.

        :param label_column_name: The column containing the label values.
        :param value_column_name: The column containing the bar values.
        :param domain: A 2-tuple containing the minimum and maximum values for
            the chart's x-axis. The domain must be large enough to contain all
            values in the column.
        :param width: The width, in characters, to use for the bar chart.
            Defaults to `120`.
        :param output: A file-like object to print to. Defaults to
            :code:`sys.stdout`.
        """
        print_bars(self, label_column_name, value_column_name, domain, width, output)
