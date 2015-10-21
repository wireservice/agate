#!/usr/bin/env python

"""
This module contains the :class:`Table` object, which is the central data
structure in :code:`agate`. Tables are created by supplying row data, column
names and subclasses of :class:`.DataType` to the constructor. Once
instantiated, tables are **immutable**. This concept is central to agate. The
data of the table may not be accessed or modified directly.

Various methods on the :class:`Table` simulate "SQL-like" operations. For
example, the :meth:`Table.select` method reduces the table to only the
specified columns. The :meth:`Table.where` method reduces the table to only
those rows that pass a truth test. And the :meth:`Table.order_by` method sorts
the rows in the table. In all of these cases the output is new :class:`Table`
and the existing table remains unmodified.

Tables are not themselves iterable, but the columns of the table can be
accessed via :attr:`Table.columns` and the rows via :attr:`Table.rows`. Both
sequences can be accessed either by numeric index or by name. (In the case of
rows, row names are optional.)
"""

from collections import Sequence
from copy import copy
from itertools import chain
import sys

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

from babel.numbers import format_decimal

try:
    import csvkit as csv
except ImportError: #pragma: no cover
    import csv

import six
from six.moves import range, zip #pylint: disable=W0622

from agate.aggregations import Min, Max
from agate.columns import Column
from agate.data_types import TypeTester, DataType, Text, Number
from agate.computations import Computation
from agate.mapped_sequence import MappedSequence
from agate.preview import print_table, print_bars
from agate.rows import Row
from agate.utils import NullOrder, Patchable, max_precision, make_number_formatter, round_limits

def allow_tableset_proxy(func):
    """
    Decorator to flag that a given Table method can be proxied as a :class:`TableSet` method.
    """
    func.allow_tableset_proxy = True

    return func

class Table(Patchable):
    """
    A dataset consisting of rows and columns. Columns refer to "vertical" slices
    of data that must all be of the same type. Rows refer to "horizontal" slices
    of data that may (and usually do) contain mixed types.

    The sequence of :class:`.Column` instances are retrieved via the
    :attr:`Table.columns` property. They may be accessed by either numeric
    index or by unique column name.

    The sequence of :class:`.Row` instances are retrieved via the
    :attr:`Table.rows` property. They maybe be accessed by either numeric index
    or, if specified, unique row names.

    :param rows: The data as a sequence of any sequences: tuples, lists, etc. If
        any row has fewer values than the number of columns, it will be filled
        out with nulls. No row may have more values than the number of columns.
    :param column_info: A sequence of pairs of column names and types. Column
        names must be strings and column types must be instances of
        :class:`.DataType`. Alternately, a sequence of :class:`.Column`
        instances. New column instances will be created reusing the name and
        data type from each column.
    :param row_names: Specifies unique names for each row. This parameter is
        optional. If specified it may be 1) the name of a single column that
        contains a unique identifier for each row, 2) a key function that takes
        a :class:`.Row` and returns a unique identifier or 3) a sequence of
        unique identifiers of the same length as the sequence of rows.
    :param _is_fork: Used internally to skip certain validation steps when data
        is propagated from an existing table. When :code:`True`, rows are
        assumed to be :class:`.Row` instances, rather than raw data.
    """
    def __init__(self, rows, column_info, row_names=None, _is_fork=False):
        column_info = list(column_info)

        if isinstance(column_info[0], Column):
            self._column_names = tuple(c.name for c in column_info)
            self._column_types = tuple(c.data_type for c in column_info)
        else:
            self._column_names, self._column_types = zip(*column_info)

            # Validation
            for column_name in self._column_names:
                if not isinstance(column_name, six.string_types):
                    raise ValueError('Column names must be strings.')

            for column_type in self._column_types:
                if not isinstance(column_type, DataType):
                    raise ValueError('Column types must be instances of DataType.')

            len_column_names = len(self._column_names)

            if len(set(self._column_names)) != len_column_names:
                raise ValueError('Duplicate column names are not allowed.')

        if not _is_fork:
            new_rows = []
            cast_funcs = [c.cast for c in self._column_types]

            for i, row in enumerate(rows):
                len_row = len(row)

                if len_row > len_column_names:
                    raise ValueError('Row %i has %i values, but Table only has %i columns.' % (i, len_row, len_column_names))
                elif len(row) < len_column_names:
                    row = chain(row, [None] * (len(self.column_names) - len_row))

                new_rows.append(Row(tuple(cast_funcs[i](d) for i, d in enumerate(row)), self._column_names))
        else:
            new_rows = rows

        if row_names:
            computed_row_names = []

            if isinstance(row_names, six.string_types):
                for row in new_rows:
                    name = row[row_names]
                    computed_row_names.append(name)
            elif hasattr(row_names, '__call__'):
                for row in new_rows:
                    name = row_names(row)
                    computed_row_names.append(name)
            elif isinstance(row_names, Sequence):
                computed_row_names = row_names
            else:
                raise ValueError('row_names must be a column name, function or sequence')

            self._row_names = tuple(computed_row_names)
        else:
            self._row_names = None

        self._rows = MappedSequence(new_rows, self._row_names)

        # Build columns
        new_columns = []

        for i, (name, data_type) in enumerate(zip(self._column_names, self._column_types)):
            column = Column(i, name, data_type, self._rows, row_names=self._row_names)
            new_columns.append(column)

        self._columns = MappedSequence(new_columns, self._column_names)

    def _fork(self, rows, column_info=None, row_names=None):
        """
        Create a new table using the metadata from this one.
        Used internally by functions like :meth:`order_by`.
        """
        if column_info is None:
            column_info = self._columns

        if row_names is None:
            row_names = self._row_names

        return Table(rows, column_info, row_names=row_names, _is_fork=True)

    @classmethod
    def from_csv(cls, path, column_info=None, row_names=None, header=True, **kwargs):
        """
        Create a new table for a CSV. This method will use csvkit if it is
        available, otherwise it will use Python's builtin csv module.

        ``kwargs`` will be passed through to :meth:`csv.reader`.

        If you are using Python 2 and not using csvkit, this method is not
        unicode-safe.

        :param path: Filepath or file-like object from which to read CSV data.
        :param column_info: May be any valid input to :meth:`Table.__init__` or
            an instance of :class:`.TypeTester`. Or, None, in which case a
            generic :class:`.TypeTester` will be created.
        :param row_names: See :meth:`Table.__init__`.
        :param header: If `True`, the first row of the CSV is assumed to contains
            headers and will be skipped.
        """
        if column_info is None:
            column_info = TypeTester()

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

        return Table(rows, column_info, row_names=row_names)

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

            for row in self._rows:
                writer.writerow(row)
        finally:
            f.close()

    @property
    def column_types(self):
        """
        Get an ordered sequence of this table's column types.

        :returns: A sequence of :class:`.DataType` instances.
        """
        return self._column_types

    @property
    def column_names(self):
        """
        Get an ordered sequence of this table's column names.
        """
        return self._column_names

    @property
    def row_names(self):
        """
        Get an ordered sequence of this table's row names.
        """
        return self._row_names

    @property
    def columns(self):
        """
        Get this tables' :class:`.MappedSequence` of columns.
        """
        return self._columns

    @property
    def rows(self):
        """
        Get this tables' :class:`.MappedSequence` of rows.
        """
        return self._rows

    @allow_tableset_proxy
    def select(self, selected_names):
        """
        Reduce this table to only the specified columns.

        :param selected_names: A sequence of names of columns to include in the
            new table.
        :returns: A new :class:`Table`.
        """
        new_columns = [self.columns[name] for name in selected_names]
        new_rows = []

        for row in self._rows:
            new_rows.append(Row(tuple(row[n] for n in selected_names), selected_names))

        return self._fork(new_rows, new_columns)

    @allow_tableset_proxy
    def where(self, test):
        """
        Filter a to only those rows where the row passes a truth test.

        :param test: A function that takes a :class:`.Row` and returns
            :code:`True` if it should be included.
        :type test: :class:`function`
        :returns: A new :class:`Table`.
        """
        rows = []

        if self._row_names is not None:
            row_names = []
        else:
            row_names = None

        for i, row in enumerate(self._rows):
            if test(row):
                rows.append(row)

                if self._row_names is not None:
                    row_names.append(self._row_names[i])

        return self._fork(rows, row_names=row_names)

    @allow_tableset_proxy
    def find(self, test):
        """
        Find the first row that passes a truth test.

        :param test: A function that takes a :class:`.Row` and returns
            :code:`True` if it matches.
        :type test: :class:`function`
        :returns: A single :class:`.Row` or :code:`None` if not found.
        """
        for row in self._rows:
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

        def sort_key(data):
            row = data[1]

            if key_is_row_function:
                k = key(row)
            else:
                k = row[key]

            if k is None:
                return NullOrder()

            return k

        results = sorted(enumerate(self._rows), key=sort_key, reverse=reverse)

        indices, rows = zip(*results)

        if self._row_names is not None:
            row_names = [self._row_names[i] for i in indices]
        else:
            row_names = None

        return self._fork(rows, row_names=row_names)

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
            s = slice(start_or_stop, stop, step)
        else:
            s = slice(start_or_stop)
        rows = self._rows[s]

        if self._row_names is not None:
            row_names = self._row_names[s]
        else:
            row_names = None

        return self._fork(rows, row_names=row_names)

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

        if self._row_names is not None:
            row_names = []
        else:
            row_names = None

        for i, row in enumerate(self._rows):
            if key_is_row_function:
                k = key(row)
            elif key is None:
                k = tuple(row)
            else:
                k = row[key]

            if k not in uniques:
                uniques.append(k)
                rows.append(row)

                if self._row_names is not None:
                    row_names.append(self._row_names[i])

        return self._fork(rows, row_names=row_names)

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
        right_key_index = None

        if left_key_is_row_function:
            left_data = [left_key(row) for row in self.rows]
        else:
            left_data = self._columns[left_key].values()

        if right_key_is_row_function:
            right_data = [right_key(row) for row in right_table.rows]
        else:
            right_column = right_table.columns[right_key]
            right_data = right_column.values()
            right_key_index = right_table.columns._keys.index(right_key)

        # Build names and type lists
        column_names = list(self._column_names)
        column_types = list(self._column_types)

        for column in right_table.columns:
            name = column.name

            if name == right_key:
                continue

            if name in self._column_names:
                column_names.append('%s2' % name)
            else:
                column_names.append(name)

            column_types.append(column.data_type)

        right_hash = {}

        for i, value in enumerate(right_data):
            if value not in []:
                right_hash[value] = []

            right_hash[value].append(self._rows[i])

        # Collect new rows
        rows = []

        if self._row_names is not None:
            row_names = []
        else:
            row_names = None

        # Iterate over left column
        for left_index, left_value in enumerate(left_data):
            new_row = list(self._rows[left_index])

            matching_rows = right_hash.get(left_value, None)

            # Rows with matches
            if matching_rows:
                for right_row in matching_rows:
                    for k, v in enumerate(right_row):
                        if k == right_key_index:
                            continue

                        new_row.append(v)

                    rows.append(Row(new_row, column_names))

                    if self._row_names is not None:
                        row_names.append(self._row_names[left_index])
            # Rows without matches
            elif not inner:
                for k, v in enumerate(right_table.column_names):
                    if k == right_key_index:
                        continue

                    new_row.append(None)

                rows.append(Row(new_row, column_names))

                if self._row_names is not None:
                    row_names.append(self._row_names[left_index])

        return self._fork(rows, zip(column_names, column_types), row_names=row_names)

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

        rows = list(chain(*[table.rows for table in tables]))

        return Table(rows, tables[0].columns, row_names=tables[0].row_names, _is_fork=True)

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
            column = self._columns[key]

            key_name = key_name or column.name
            key_type = key_type or column.data_type

        groups = OrderedDict()

        for row in self._rows:
            if key_is_row_function:
                group_name = key(row)
            else:
                group_name = row[column.name]

            group_name = key_type.cast(group_name)

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append(row)

        output = OrderedDict()

        for group, rows in groups.items():
            output[group] = self._fork(rows)

        return TableSet(output.values(), output.keys(), key_name=key_name, key_type=key_type)

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

        for row in self._rows:
            new_columns = tuple(c.run(row) for c, n in computations)
            new_rows.append(Row(tuple(row) + new_columns, column_names))

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
            column = self._columns[key]

            key_name = key_name or column.name
            key_type = key_type or column.data_type

        output = OrderedDict()

        for row in self._rows:
            if key_is_row_function:
                group_name = key(row)
            else:
                group_name = row[key_name]

            group_name = key_type.cast(group_name)

            if group_name not in output:
                output[group_name] = 0

            output[group_name] += 1

        column_names = [key_name, 'count']
        column_types = [key_type, Number()]

        return Table(output.items(), zip(column_names, column_types), row_names=tuple(output.keys()))

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
        column = self._columns[column_name]

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

        for row in self._rows:
            value = row[column_name]

            if value is None:
                try:
                    bins[None] += 1
                except KeyError:
                    bins[None] = Decimal('1')

                continue    # pragma: no cover

            i = 1

            try:
                while value >= breaks[i]:
                    i += 1
            except IndexError:
                i -= 1

            last_exclusive = (i == len(breaks) - 1)
            name = name_bin(breaks[i - 1], breaks[i], last_exclusive=last_exclusive)

            bins[name] += 1

        return Table(bins.items(), [(column_name, Text()), ('count', Number())], row_names=tuple(bins.keys()))

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
