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

import codecs
from collections import OrderedDict, Sequence
from copy import copy
from itertools import chain
import json
import sys
import os.path

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

from babel.numbers import format_decimal

import six
from six.moves import range, zip, zip_longest #pylint: disable=W0622

from agate.aggregations import Min, Max
from agate.columns import Column
from agate.data_types import TypeTester, DataType, Text, Number
from agate.mapped_sequence import MappedSequence
from agate.preview import print_table, print_html, print_bars, print_structure
from agate.rows import Row
from agate import utils

if six.PY2:   #pragma: no cover
    from agate import csv_py2 as csv
else:
    from agate import csv_py3 as csv

def allow_tableset_proxy(func):
    """
    Decorator to flag that a given Table method can be proxied as a :class:`TableSet` method.
    """
    func.allow_tableset_proxy = True

    return func

@six.python_2_unicode_compatible
class Table(utils.Patchable):
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

    :param rows:
        The data as a sequence of any sequences: tuples, lists, etc. If
        any row has fewer values than the number of columns, it will be filled
        out with nulls. No row may have more values than the number of columns.
    :param column_names:
        A sequence of string names for each column or `None`, in which case
        column names will be automatically assigned using :func:`.letter_name`.
    :param column_types:
        A sequence of instances of :class:`.DataType` or an instance of
        :class:`.TypeTester` or `None` in which case a generic TypeTester will
        be used.
    :param row_names:
        Specifies unique names for each row. This parameter is
        optional. If specified it may be 1) the name of a single column that
        contains a unique identifier for each row, 2) a key function that takes
        a :class:`.Row` and returns a unique identifier or 3) a sequence of
        unique identifiers of the same length as the sequence of rows. The
        uniqueness of resulting identifiers is not validated, so be certain
        the values you provide are truly unique.
    :param _is_fork:
        Used internally to skip certain validation steps when data
        is propagated from an existing table. When :code:`True`, rows are
        assumed to be :class:`.Row` instances, rather than raw data.
    """
    def __init__(self, rows, column_names=None, column_types=None, row_names=None, _is_fork=False):
        # Validate column names
        if column_names:
            final_column_names = []

            for i, column_name in enumerate(column_names):
                if column_name is None:
                    final_column_names.append(utils.letter_name(i))
                elif isinstance(column_name, six.string_types):
                    final_column_names.append(column_name)
                else:
                    raise ValueError('Column names must be strings or None.')

            if len(set(final_column_names)) != len(final_column_names):
                raise ValueError('Duplicate column names are not allowed.')

            self._column_names = tuple(final_column_names)
        else:
            self._column_names = tuple(utils.letter_name(i) for i in range(len(rows[0])))

        len_column_names = len(self._column_names)

        # Validate column_types
        if column_types is None:
            column_types = TypeTester()
        elif isinstance(column_types, TypeTester):
            pass
        else:
            for column_type in column_types:
                if not isinstance(column_type, DataType):
                    raise ValueError('Column types must be instances of DataType.')

        if isinstance(column_types, TypeTester):
            self._column_types = column_types.run(rows, self._column_names)
        else:
            self._column_types = tuple(column_types)

        if len_column_names != len(self._column_types):
            raise ValueError('column_names and column_types must be the same length.')

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

    def __str__(self):
        """
        Print the table's structure via :meth:`Table.print_structure`.
        """
        structure = six.StringIO()

        self.print_structure(output=structure)

        return structure.getvalue()

    @property
    def column_types(self):
        """
        Get an ordered sequence of this table's column types.

        :returns:
            A tuple of :class:`.DataType` instances.
        """
        return self._column_types

    @property
    def column_names(self):
        """
        Get an ordered sequence of this table's column names.

        :returns:
            A tuple of strings.
        """
        return self._column_names

    @property
    def row_names(self):
        """
        Get an ordered sequence of this table's row names.

        :returns:
            A tuple of strings if this table has row names. Otherwise, `None`.
        """
        return self._row_names

    @property
    def columns(self):
        """
        Get this table's columns.

        :returns:
            :class:`.MappedSequence`
        """
        return self._columns

    @property
    def rows(self):
        """
        Get this table's rows.

        :returns:
            :class:`.MappedSequence`
        """
        return self._rows

    def _fork(self, rows, column_names=None, column_types=None, row_names=None):
        """
        Create a new table using the metadata from this one. Used internally by
        functions like :meth:`order_by`.

        :param rows:
            Row data for the forked table.
        :param column_names:
            Column names for the forked table. If not specified, fork will use
            this table's column names.
        :param column_types:
            Column types for the forked table. If not specified, fork will use
            this table's column names.
        :param row_names:
            Row names for the forked table. If not specified, fork will use
            this table's row names.
        """
        if column_names is None:
            column_names = self._column_names

        if column_types is None:
            column_types = self._column_types

        if row_names is None:
            row_names = self._row_names

        return Table(rows, column_names, column_types, row_names=row_names, _is_fork=True)

    def rename(self, column_names=None, row_names=None):
        """
        Creates a copy of this table with different column or row names.

        :param column_names:
            New column names for the renamed table. May be either an array or
            a dictionary mapping existing column names to new names. If not
            specified, will use this table's existing column names.
        :param row_names:
            New row names for the renamed table. May be either an array or
            a dictionary mapping existing row names to new names. If not
            specified, will use this table's existing row names.
        """
        if isinstance(column_names, dict):
            column_names = [column_names[name] if name in column_names else name for name in self.column_names]

        if isinstance(row_names, dict):
            row_names = [row_names[name] if name in row_names else name for name in self.row_names]

        if column_names is not None and column_names != self.column_names:
            if row_names is None:
                row_names = self._row_names

            return Table(self.rows, column_names, self.column_types, row_names=row_names, _is_fork=False)
        else:
            return self._fork(self.rows, column_names, self._column_types, row_names=row_names)

    @classmethod
    def from_csv(cls, path, column_names=None, column_types=None, row_names=None, header=True, **kwargs):
        """
        Create a new table for a CSV. This method uses agate's builtin
        CSV reader, which supports unicode on both Python 2 and Python 3.

        `kwargs` will be passed through to the CSV reader.

        :param path:
            Filepath or file-like object from which to read CSV data.
        :param column_names:
            See :meth:`Table.__init__`.
        :param column_types:
            See :meth:`Table.__init__`.
        :param row_names:
            See :meth:`Table.__init__`.
        :param header:
            If `True`, the first row of the CSV is assumed to contains headers
            and will be skipped. If `header` and `column_names` are both
            specified then a row will be skipped, but `column_names` will be
            used.
        """
        if hasattr(path, 'read'):
            rows = list(csv.reader(path, **kwargs))
        else:
            with open(path) as f:
                rows = list(csv.reader(f, **kwargs))

        if header:
            if column_names is None:
                column_names = rows.pop(0)
            else:
                rows.pop(0)

        return Table(rows, column_names, column_types, row_names=row_names)

    def to_csv(self, path, **kwargs):
        """
        Write this table to a CSV. This method uses agate's builtin CSV writer,
        which supports unicode on both Python 2 and Python 3.

        `kwargs` will be passed through to the CSV writer.

        :param path:
            Filepath or file-like object to write to.
        """
        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        close = True
        f = None

        try:
            if hasattr(path, 'write'):
                f = path
                close = False
            else:
                dirpath = os.path.dirname(path)

                if dirpath and not os.path.exists(dirpath):
                    os.makedirs(dirpath)

                f = open(path, 'w')

            writer = csv.writer(f, **kwargs)
            writer.writerow(self._column_names)

            csv_funcs = [c.csvify for c in self._column_types]

            for row in self._rows:
                writer.writerow(tuple(csv_funcs[i](d) for i, d in enumerate(row)))
        finally:
            if close and f is not None:
                f.close()

    @classmethod
    def from_json(cls, path, row_names=None, key=None, newline=False, **kwargs):
        """
        Create a new table from a JSON file. Contents should be an array
        containing a dictionary for each "row". Nested objects or lists will
        also be parsed. For example, this object:

        .. code-block:: javascript

            {
                'one': {
                    'a': 1,
                    'b': 2,
                    'c': 3
                },
                'two': [4, 5, 6],
                'three': 'd'
            }

        Would generate these columns and values:

        .. code-block:: python

            {
                'one/a': 1,
                'one/b': 2,
                'one/c': 3,
                'two.0': 4,
                'two.1': 5,
                'two.2': 6,
                'three': 'd'
            }

        Column names and types will be inferred from the data. Not all rows are
        required to have the same keys. Missing elements will be filled in with
        null.

        If the file contains a top-level dictionary you may specify what
        property contains the row list using the `key` parameter.

        `kwargs` will be passed through to :meth:`json.load`.

        :param path:
            Filepath or file-like object from which to read CSV data.
        :param row_names:
            See :meth:`Table.__init__`.
        :param key:
            The key of the top-level dictionary that contains a list of row
            arrays.
        :param newline:
            If `True` then the file will be parsed as "newline-delimited JSON".
        """
        if newline:
            js = []

            if hasattr(path, 'read'):
                for line in path:
                    js.append(json.loads(line, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs))
            else:
                with open(path, 'r') as f:
                    for line in f:
                        js.append(json.loads(line, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs))
        else:
            if hasattr(path, 'read'):
                js = json.load(path, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)
            else:
                with open(path, 'r') as f:
                    js = json.load(f, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)

        if isinstance(js, dict):
            if not key:
                raise TypeError('When converting a JSON document with a top-level dictionary element, a key must be specified.')

            js = js[key]

        column_names = []
        row_objects = []

        for obj in js:
            parsed = utils.parse_object(obj)

            for key in parsed.keys():
                if key not in column_names:
                    column_names.append(key)

            row_objects.append(parsed)

        rows = []

        for obj in row_objects:
            r = []

            for name in column_names:
                r.append(obj.get(name, None))

            rows.append(r)

        return Table(rows, column_names, row_names=row_names)

    def to_json(self, path, key=None, newline=False, indent=None, **kwargs):
        """
        Write this table to a JSON file or file-like object.

        `kwargs` will be passed through to the JSON encoder.

        :param path:
            File path or file-like object to write to.
        :param key:
            If specified, JSON will be output as an hash instead of a list. May
            be either the name of a column from the this table containing
            unique values or a :class:`function` that takes a row and returns
            a unique value.
        :param newline:
            If `True`, output will be in the form of "newline-delimited JSON".
        :param indent:
            If specified, the number of spaces to indent the JSON for
            formatting.
        """
        if key is not None and newline:
            raise ValueError('key and newline may not be specified together.')

        if newline and indent is not None:
            raise ValueError('newline and indent may not be specified together.')

        key_is_row_function = hasattr(key, '__call__')

        json_kwargs = {
            'ensure_ascii': False,
            'indent': indent
        }

        if six.PY2:
            json_kwargs['encoding'] = 'utf-8'

        # Pass remaining kwargs through to JSON encoder
        json_kwargs.update(kwargs)

        json_funcs = [c.jsonify for c in self._column_types]

        close = True
        f = None

        try:
            if hasattr(path, 'write'):
                f = path
                close = False
            else:
                if os.path.dirname(path) and not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                f = open(path, 'w')

            if six.PY2:
                f = codecs.getwriter('utf-8')(f)

            def dump_json(data):
                json.dump(data, f, **json_kwargs)

                if newline:
                    f.write('\n')

            # Keyed
            if key is not None:
                output = OrderedDict()

                for row in self._rows:
                    if key_is_row_function:
                        k = key(row)
                    else:
                        k = row[key]

                    if k in output:
                        raise ValueError('Value %s is not unique in the key column.' % six.text_type(k))

                    values = tuple(json_funcs[i](d) for i, d in enumerate(row))
                    output[k] = OrderedDict(zip(row.keys(), values))
                dump_json(output)
            # Newline-delimited
            elif newline:
                for row in self._rows:
                    values = tuple(json_funcs[i](d) for i, d in enumerate(row))
                    dump_json(OrderedDict(zip(row.keys(), values)))
            # Normal
            else:
                output = []

                for row in self._rows:
                    values = tuple(json_funcs[i](d) for i, d in enumerate(row))
                    output.append(OrderedDict(zip(row.keys(), values)))

                dump_json(output)
        finally:
            if close and f is not None:
                f.close()

    @allow_tableset_proxy
    def select(self, selected_column_names):
        """
        Create a new table with the same rows as this one, but only those
        columns in the ``selected_column_names`` sequence.

        :param selected_column_names:
            A sequence of names of columns to include in the new table.
        :returns:
            A new :class:`Table`.
        """
        column_types = [self.columns[name].data_type for name in selected_column_names]
        new_rows = []

        for row in self._rows:
            new_rows.append(Row(tuple(row[n] for n in selected_column_names), selected_column_names))

        return self._fork(new_rows, selected_column_names, column_types)

    @allow_tableset_proxy
    def exclude(self, excluded_column_names):
        """
        Create a new table with the same rows as this one, but only columns
        not in the ``excluded_column_names`` sequence.

        :param excluded_column_names:
            A sequence of names of columns to exclude from the new table.
        :returns:
            A new :class:`Table`.
        """
        selected_column_names = [n for n in self._column_names if n not in excluded_column_names]

        return self.select(selected_column_names)

    @allow_tableset_proxy
    def where(self, test):
        """
        Filter a to only those rows where the row passes a truth test.

        :param test:
            A function that takes a :class:`.Row` and returns :code:`True` if
            it should be included.
        :type test:
            :class:`function`
        :returns:
            A new :class:`Table`.
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

        :param test:
            A function that takes a :class:`.Row` and returns :code:`True` if
            it matches.
        :type test:
            :class:`function`
        :returns:
            A single :class:`.Row` if found, or `None`.
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

        :param key:
            Either the name of a column to sort by or a :class:`function` that
            takes a row and returns a value to sort by.
        :param reverse:
            If `True` then sort in reverse (typically, descending) order.
        :returns:
            A new :class:`Table`.
        """
        key_is_row_function = hasattr(key, '__call__')

        def sort_key(data):
            row = data[1]

            if key_is_row_function:
                k = key(row)
            else:
                k = row[key]

            if k is None:
                return utils.NullOrder()

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

        :param start_or_stop:
            If the only argument, then how many rows to include, otherwise,
            the index of the first row to include.
        :param stop:
            The index of the last row to include.
        :param step:
            The size of the jump between rows to include. (`step=2` will return
            every other row.)
        :returns:
            A new :class:`Table`.
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

        :param key:
            Either 1) the name of a column to use to identify unique rows or 2)
            a :class:`function` that takes a row and returns a value to
            identify unique rows or 3) `None`, in which case the entire row
            will be checked for uniqueness.
        :returns:
            A new :class:`Table`.
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

        :param right_table:
            The "right" table to join to.
        :param left_key:
            Either the name of a column from the this table to join on, or a
            :class:`function` that takes a row and returns a value to join on.
        :param right_key:
            Either the name of a column from :code:table` to join on, or a
            :class:`function` that takes a row and returns a value to join on.
            If :code:`None` then :code:`left_key` will be used for both.
        :param inner:
            Perform a SQL-style "inner join" instead of a left outer join. Rows
            which have no match for :code:`left_key` will not be included in
            the output table.
        :returns:
            A new :class:`Table`.
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
            if value not in right_hash:
                right_hash[value] = []

            right_hash[value].append(right_table._rows[i])

        # Collect new rows
        rows = []

        if self._row_names is not None:
            row_names = []
        else:
            row_names = None

        # Iterate over left column
        for left_index, left_value in enumerate(left_data):
            matching_rows = right_hash.get(left_value, None)

            # Rows with matches
            if matching_rows:
                for right_row in matching_rows:
                    new_row = list(self._rows[left_index])

                    for k, v in enumerate(right_row):
                        if k == right_key_index:
                            continue

                        new_row.append(v)

                    rows.append(Row(new_row, column_names))

                    if self._row_names is not None:
                        row_names.append(self._row_names[left_index])
            # Rows without matches
            elif not inner:
                new_row = list(self._rows[left_index])

                for k, v in enumerate(right_table.column_names):
                    if k == right_key_index:
                        continue

                    new_row.append(None)

                rows.append(Row(new_row, column_names))

                if self._row_names is not None:
                    row_names.append(self._row_names[left_index])

        return self._fork(rows, column_names, column_types, row_names=row_names)

    @classmethod
    def merge(cls, tables, row_names=None):
        """
        Merge an array of tables with identical columns into a single table.
        Each table must have exactly the same column types. Their column names
        need not be identical. The first table's column names will be the ones
        which are used.

        Row names will be lost, but new row names can be specified with the
        `row_names` argument.

        :param tables:
            An sequence of :class:`Table` instances.
        :param row_names:
            See :class:`Table` for the usage of this parameter.
        :returns:
            A new :class:`Table`.
        """
        column_names = tables[0].column_names
        column_types = tables[0].column_types

        for table in tables[1:]:
            if any(not isinstance(a, type(b)) for a,b in zip_longest(table.column_types, column_types)):
                raise ValueError('Only tables with identical column types may be merged.')

        rows = []

        for table in tables:
            if table.column_names == column_names:
                rows.extend(table.rows)
            else:
                for row in table.rows:
                    rows.append(Row(row.values(), column_names))

        return Table(rows, column_names, column_types, row_names=row_names, _is_fork=True)

    @allow_tableset_proxy
    def group_by(self, key, key_name=None, key_type=None):
        """
        Create a new :class:`Table` for unique value and return them as a
        :class:`.TableSet`. The :code:`key` can be either a column name
        or a function that returns a value to group by.

        Note that when group names will always be coerced to a string,
        regardless of the format of the input column.

        :param key:
            Either the name of a column from the this table to group by, or a
            :class:`function` that takes a row and returns a value to group by.
        :param key_name:
            A name that describes the grouped properties. Defaults to the
            column name that was grouped on or "group" if grouping with a key
            function. See :class:`.TableSet` for more.
        :param key_type:
            An instance some subclass of :class:`.DataType`. If not provided
            it will default to a :class`.Text`.
        :returns:
            A :class:`.TableSet` mapping where the keys are unique values from
            the :code:`key` and the values are new :class:`Table` instances
            containing the grouped rows.
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

    def aggregate(self, aggregations):
        """
        Aggregate data from the columns in this table by applying a sequence of
        :class:`.Aggregation` instances.

        :param aggregations:
            A single :class:`.Aggregation` instance or sequence of them.
        :returns:
            If the input was a single :class:`Aggregation` then a single result
            will be returned. If it was a sequence then a tuple of results will
            be returned.
        """
        if isinstance(aggregations, Sequence):
            results = []

            for agg in aggregations:
                agg.validate(self)

            for agg in aggregations:
                results.append(agg.run(self))

            return tuple(results)
        else:
            aggregations.validate(self)

            return aggregations.run(self)

    @allow_tableset_proxy
    def compute(self, computations):
        """
        Compute new columns by applying one or more :class:`.Computation` to
        each row.

        :param computations:
            A sequence of pairs of new column names and :class:`.Computation`
            instances.
        :returns:
            A new :class:`Table`.
        """
        column_names = list(copy(self._column_names))
        column_types = list(copy(self._column_types))

        for new_column_name, computation in computations:
            column_names.append(new_column_name)
            column_types.append(computation.get_computed_data_type(self))

            computation.validate(self)

        new_columns = tuple(c.run(self) for n, c in computations)
        new_rows = []

        for i, row in enumerate(self._rows):
            values = tuple(row) + tuple(c[i] for c in new_columns)
            new_rows.append(Row(values, column_names))

        return self._fork(new_rows, column_names, column_types)

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

        :param key:
            Either the name of a column from the this table to count, or a
            :class:`function` that takes a row and returns a value to count.
        :param key_name:
            A name that describes the counted properties. Defaults to the
            column name that was counted or "group" if counting with a key
            function.
        :param key_type:
            An instance some subclass of :class:`.DataType`. If not provided
            it will default to a :class`.Text`.
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

        return Table(output.items(), column_names, column_types, row_names=tuple(output.keys()))

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

        :param column_name:
            The name of the column to bin. Must be of type :class:`.Number`
        :param count:
            The number of bins to create. If not specified then each value will
            be counted as its own bin.
        :param start:
            The minimum value to start the bins at. If not specified the
            minimum value in the column will be used.
        :param end:
            The maximum value to end the bins at. If not specified the maximum
            value in the column will be used.
        :returns:
            A new :class:`Table`.
        """
        if start is None or end is None:
            start, end = utils.round_limits(
                Min(column_name).run(self),
                Max(column_name).run(self)
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

        decimal_places = utils.max_precision(breaks)
        break_formatter = utils.make_number_formatter(decimal_places)

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

        column_names = [column_name, 'count']
        column_types = [Text(), Number()]

        return Table(bins.items(), column_names, column_types, row_names=tuple(bins.keys()))

    def print_table(self, max_rows=None, max_columns=None, output=sys.stdout):
        """
        Print a well-formatted preview of this table to the console or any
        other output.

        :param max_rows:
            The maximum number of rows to display before truncating the data.
        :param max_columns:
            The maximum number of columns to display before truncating the data.
        :param output:
            A file-like object to print to. Defaults to :code:`sys.stdout`.
        """
        print_table(self, max_rows, max_columns, output)

    def print_html(self, max_rows=None, max_columns=None, output=sys.stdout):
        """
        Print an HTML-formatted preview of this table to the console or any
        other output.

        :param max_rows:
            The maximum number of rows to display before truncating the data.
        :param max_columns:
            The maximum number of columns to display before truncating the data.
        :param output:
            A file-like object to print to. Defaults to :code:`sys.stdout`.
        """
        print_html(self, max_rows, max_columns, output)

    def print_csv(self, **kwargs):
        """
        A shortcut for printing a CSV directly to the csonsole. Effectively the
        same as passing :meth:`sys.stdout` to :meth:`Table.to_csv`.

        `kwargs` will be passed on to :meth:`Table.to_csv`.
        """
        self.to_csv(sys.stdout, **kwargs)

    def print_json(self, **kwargs):
        """
        A shortcut for printing JSON directly to the console. Effectively the
        same as passing :meth:`sys.stdout` to :meth:`Table.to_json`.

        `kwargs` will be passed on to :meth:`Table.to_json`.
        """
        self.to_json(sys.stdout, **kwargs)

    def print_bars(self, label_column_name, value_column_name, domain=None, width=120, output=sys.stdout):
        """
        Print a text-based bar chart of the columns names `label_column_name`
        and `value_column_name`.

        :param label_column_name:
            The column containing the label values.
        :param value_column_name:
            The column containing the bar values.
        :param domain:
            A 2-tuple containing the minimum and maximum values for the chart's
            x-axis. The domain must be large enough to contain all values in
            the column.
        :param width:
            The width, in characters, to use for the bar chart. Defaults to
            `120`.
        :param output:
            A file-like object to print to. Defaults to :code:`sys.stdout`.
        """
        print_bars(self, label_column_name, value_column_name, domain, width, output)

    def print_structure(self, output=sys.stdout):
        """
        Print the column names and their respective types

        :param table:
            A :class:`Table` instance.

        :param output:
            The output used to print the structure of the :class:`Table`.

        :returns:
            None
        """
        left_column = [n for n in self.column_names]
        right_column = [t.__class__.__name__ for t in self.column_types]
        column_headers = ['column_names', 'column_types']
        
        print_structure(left_column, right_column, column_headers, output)
