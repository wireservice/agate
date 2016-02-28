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
import warnings

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

from babel.numbers import format_decimal

import six
from six.moves import range, zip  # pylint: disable=W0622

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from agate.aggregations import Count, Min, Max
from agate.columns import Column
from agate.data_types import TypeTester, DataType, Text, Number
from agate.exceptions import DataTypeError
from agate.mapped_sequence import MappedSequence
from agate.preview import print_table, print_html, print_bars, print_structure
from agate.rows import Row
from agate import utils
from agate.warns import warn_duplicate_column

if six.PY2:  # pragma: no cover
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
        if isinstance(rows, six.string_types):
            raise ValueError('When created directly, the first argument to Table must be a sequence of rows. Did you want agate.Table.from_csv?')

        # Validate column names
        if column_names:
            final_column_names = []

            for i, column_name in enumerate(column_names):
                if column_name is None:
                    new_column_name = utils.letter_name(i)
                    warnings.warn('Column name not specified. "%s" will be used as name.' % new_column_name, RuntimeWarning)
                elif isinstance(column_name, six.string_types):
                    new_column_name = column_name
                else:
                    raise ValueError('Column names must be strings or None.')

                final_column_name = new_column_name
                duplicates = 0
                while final_column_name in final_column_names:
                    final_column_name = new_column_name + '_' + str(duplicates + 2)
                    duplicates += 1

                if duplicates > 0:
                    warn_duplicate_column(new_column_name, final_column_name)

                final_column_names.append(final_column_name)

            self._column_names = tuple(final_column_names)
        elif rows:
            self._column_names = tuple(utils.letter_name(i) for i in range(len(rows[0])))
            warnings.warn('Column names not specified. "%s" will be used as names.' % str(self._column_names), RuntimeWarning, stacklevel=2)
        else:
            self._column_names = []

        len_column_names = len(self._column_names)

        # Validate column_types
        if column_types is None:
            column_types = TypeTester()
        elif not isinstance(column_types, TypeTester):
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
    def from_csv(cls, path, column_names=None, column_types=None, row_names=None, header=True, sniff_limit=0, **kwargs):
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
        :param sniff_limit:
            Limit CSV dialect sniffing to the specified number of bytes. Set to
            None to sniff the entire file. Defaults to 0 or no sniffing.
        """
        if hasattr(path, 'read'):
            contents = path.read()
        else:
            with open(path) as f:
                contents = f.read()

        if sniff_limit is None:
            kwargs['dialect'] = csv.Sniffer().sniff(contents)
        elif sniff_limit > 0:
            kwargs['dialect'] = csv.Sniffer().sniff(contents[:sniff_limit])

        rows = list(csv.reader(StringIO(contents), header=header, **kwargs))

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
    def from_json(cls, path, row_names=None, key=None, newline=False, column_types=None, **kwargs):
        """
        Create a new table from a JSON file. Once the JSON is deseralized, the
        resulting Python object is passed to :meth:`Table.from_object`. See the
        documentation of that method for additional details.

        If the file contains a top-level dictionary you may specify what
        property contains the row list using the `key` parameter.

        `kwargs` will be passed through to :meth:`json.load`.

        :param path:
            Filepath or file-like object from which to read JSON data.
        :param row_names:
            See :meth:`Table.__init__`.
        :param key:
            The key of the top-level dictionary that contains a list of row
            arrays.
        :param newline:
            If `True` then the file will be parsed as "newline-delimited JSON".
        :param column_types:
            See :meth:`Table.__init__`.
        """
        if key is not None and newline:
            raise ValueError('key and newline may not be specified together.')

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

        return Table.from_object(js, row_names=row_names, column_types=column_types)

    @classmethod
    def from_object(cls, obj, row_names=None, column_types=None):
        """
        Create a new table from a Python object with a structure that mirrors
        a deserialized JSON object. Its contents should be an array
        containing a dictionary for each "row". Nested objects or lists will
        also be parsed. For example, this object:

        .. code-block:: python

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

        :param obj:
            Filepath or file-like object from which to read JSON data.
        :param row_names:
            See :meth:`Table.__init__`.
        :param column_types:
            See :meth:`Table.__init__`.
        """
        column_names = []
        row_objects = []

        for sub in obj:
            parsed = utils.parse_object(sub)

            for key in parsed.keys():
                if key not in column_names:
                    column_names.append(key)

            row_objects.append(parsed)

        rows = []

        for sub in row_objects:
            r = []

            for name in column_names:
                r.append(sub.get(name, None))

            rows.append(r)

        return Table(rows, column_names, row_names=row_names, column_types=column_types)

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
    def select(self, key):
        """
        Create a new table with the same rows as this one, but only those
        columns in the ``key``.

        :param key:
            Either the name of a column to include or a sequence of such names.
        :returns:
            A new :class:`Table`.
        """
        if not utils.issequence(key):
            key = [key]

        column_types = [self.columns[name].data_type for name in key]
        new_rows = []

        for row in self._rows:
            new_rows.append(Row(tuple(row[n] for n in key), key))

        return self._fork(new_rows, key, column_types)

    @allow_tableset_proxy
    def exclude(self, key):
        """
        Create a new table with the same rows as this one, but only columns
        not in the ``key``.

        :param key:
            Either the name of a column to exclude or a sequence of such names.
        :returns:
            A new :class:`Table`.
        """
        if not utils.issequence(key):
            key = [key]

        selected_column_names = [n for n in self._column_names if n not in key]

        return self.select(selected_column_names)

    @allow_tableset_proxy
    def where(self, test):
        """
        Create a new table with the rows from this table that pass a truth test.

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
            Either the name of a column to sort by, a sequence of such names,
            or a :class:`function` that takes a row and returns a value to sort
            by.
        :param reverse:
            If `True` then sort in reverse (typically, descending) order.
        :returns:
            A new :class:`Table`.
        """
        if len(self._rows) == 0:
            return self._fork(self._rows)
        else:
            key_is_row_function = hasattr(key, '__call__')
            key_is_sequence = utils.issequence(key)

            def sort_key(data):
                row = data[1]

                if key_is_row_function:
                    k = key(row)
                elif key_is_sequence:
                    k = tuple(row[n] for n in key)
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
            Either the name of a column to use to identify unique rows, a
            sequence of such column names, a :class:`function` that takes a
            row and returns a value to identify unique rows, or `None`, in
            which case the entire row will be checked for uniqueness.
        :returns:
            A new :class:`Table`.
        """
        key_is_row_function = hasattr(key, '__call__')
        key_is_sequence = utils.issequence(key)

        uniques = []
        rows = []

        if self._row_names is not None:
            row_names = []
        else:
            row_names = None

        for i, row in enumerate(self._rows):
            if key_is_row_function:
                k = key(row)
            elif key_is_sequence:
                k = (row[j] for j in key)
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
    def join(self, right_table, left_key, right_key=None, inner=False, require_match=False, columns=None):
        """
        Performs the equivalent of SQL's "left outer join", combining columns
        from this table and from :code:`right_table` anywhere that the
        :code:`left_key` and :code:`right_key` are equivalent.

        Where there is no match for :code:`left_key` the left columns will
        be included with the right columns set to :code:`None` unless
        the :code:`inner` argument is specified. (See arguments for more.)

        If :code:`left_key` and :code:`right_key` are column names, only
        the left columns will be included in the output table.

        Column names from the right table which also exist in this table will
        be suffixed "2" in the new table.

        :param right_table:
            The "right" table to join to.
        :param left_key:
            Either the name of a column from the this table to join on, a
            sequence of such column names, or a :class:`function` that takes a
            row and returns a value to join on.
        :param right_key:
            Either the name of a column from :code:table` to join on, a
            sequence of such column names, or a :class:`function` that takes a
            row and returns a value to join on. If :code:`None` then
            :code:`left_key` will be used for both.
        :param inner:
            Perform a SQL-style "inner join" instead of a left outer join. Rows
            which have no match for :code:`left_key` will not be included in
            the output table.
        :param require_match:
            If true, an exception will be raised if there is a left_key with no
            matching right_key.
        :param columns:
            A sequence of column names from :code:`right_table` to include in
            the final output table. Defaults to all columns not in
            :code:`right_key`.
        :returns:
            A new :class:`Table`.
        """
        if right_key is None:
            right_key = left_key

        # Get join columns
        right_key_indices = []

        left_key_is_func = hasattr(left_key, '__call__')
        left_key_is_sequence = utils.issequence(left_key)

        # Left key is a function
        if left_key_is_func:
            left_data = [left_key(row) for row in self.rows]
        # Left key is a sequence
        elif left_key_is_sequence:
            left_columns = [self._columns[key] for key in left_key]
            left_data = zip(*[column.values() for column in left_columns])
        # Left key is a column name/index
        else:
            left_data = self._columns[left_key].values()

        right_key_is_func = hasattr(right_key, '__call__')
        right_key_is_sequence = utils.issequence(right_key)

        # Right key is a function
        if right_key_is_func:
            right_data = [right_key(row) for row in right_table.rows]
        # Right key is a sequence
        elif right_key_is_sequence:
            right_columns = [right_table.columns[key] for key in right_key]
            right_data = zip(*[column.values() for column in right_columns])
            right_key_indices = [right_table.columns._keys.index(key) for key in right_key]
        # Right key is a column name/index
        else:
            right_column = right_table.columns[right_key]
            right_data = right_column.values()
            right_key_indices = [right_table.columns._keys.index(right_key)]

        # Build names and type lists
        column_names = list(self._column_names)
        column_types = list(self._column_types)

        for i, column in enumerate(right_table.columns):
            name = column.name

            if columns is None and i in right_key_indices:
                continue

            if columns is not None and name not in columns:
                continue

            if name in self._column_names:
                column_names.append('%s2' % name)
            else:
                column_names.append(name)

            column_types.append(column.data_type)

        if columns is not None:
            right_table = right_table.select([n for n in right_table._column_names if n in columns])

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

            if require_match and matching_rows is None:
                raise ValueError('Left key "%s" does not have a matching right key.' % left_value)

            # Rows with matches
            if matching_rows:
                for right_row in matching_rows:
                    new_row = list(self._rows[left_index])

                    for k, v in enumerate(right_row):
                        if columns is None and k in right_key_indices:
                            continue

                        new_row.append(v)

                    rows.append(Row(new_row, column_names))

                    if self._row_names is not None:
                        row_names.append(self._row_names[left_index])
            # Rows without matches
            elif not inner:
                new_row = list(self._rows[left_index])

                for k, v in enumerate(right_table.column_names):
                    if columns is None and k in right_key_indices:
                        continue

                    new_row.append(None)

                rows.append(Row(new_row, column_names))

                if self._row_names is not None:
                    row_names.append(self._row_names[left_index])

        return self._fork(rows, column_names, column_types, row_names=row_names)

    @allow_tableset_proxy
    def homogenize(self, key, compare_values, default_row=None):
        """
        Fills missing rows in a dataset with default values.

        Determines what rows are missing by comparing the values in the given
        column_names with the expected compare_values.

        Values not found in the table will be used to generate new rows with
        the given default_row.

        Default_row should be an array of values or an array-generating
        function. If not specified, the new rows will have `None` in columns
        not given in column_names.

        If it is an array of values, the length should be row length minus
        column_names count and the gap will be filled with the missing values.

        If it is an array-generating function, the function should take an array
        of missing values for each new row and output a full row including those
        values.

        :param key:
            Either a column name or a sequence of such names.
        :param compare_values:
            An array of lists with combinations of values that should be present
            in at least one row in the table. A row is generated for each
            combination not found.
        :param default_row:
            An array of values or a function to generate new rows. The length of
            the input array should be equal to row length minus column_names
            count. The length of array generated by the function should be the
            row length.
        :returns:
            A new :class:`Table`.
        """
        rows = list(self._rows)

        if not utils.issequence(key):
            key = [key]

        column_values = [self._columns.get(name) for name in key]
        column_indexes = [self._column_names.index(name) for name in key]

        column_values = zip(*column_values)
        differences = list(set(map(tuple, compare_values)) - set(column_values))

        for difference in differences:
            if callable(default_row):
                rows.append(Row(default_row(difference), self._column_names))
            else:
                if default_row is not None:
                    new_row = default_row
                else:
                    new_row = [None] * (len(self._column_names) - len(key))

                for i, d in zip(column_indexes, difference):
                    new_row.insert(i, d)

                rows.append(Row(new_row, self._column_names))

        return self._fork(rows, self._column_names, self._column_types)

    @classmethod
    def merge(cls, tables, row_names=None, column_names=None):
        """
        Merge an array of tables into a single table.

        Row names will be lost, but new row names can be specified with the
        `row_names` argument.

        It is possible to limit the columns included in the new :class:`Table`
        with `column_names` argument. For example, to only include columns from
        a specific table, set `column_names` equal to `table.column_names`.

        :param tables:
            An sequence of :class:`Table` instances.
        :param row_names:
            See :class:`Table` for the usage of this parameter.
        :param column_names:
            A sequence of column names to include in the new :class:`Table`. If
            not specified, all distinct column names from `tables` are included.
        :returns:
            A new :class:`Table`.
        """
        new_columns = OrderedDict()

        for table in tables:
            for i in range(0, len(table.columns)):
                if column_names is None or table.column_names[i] in column_names:
                    column_name = table.column_names[i]
                    column_type = table.column_types[i]

                    if column_name in new_columns:
                        if not isinstance(column_type, type(new_columns[column_name])):
                            raise DataTypeError('Tables contain columns with the same names, but different types.')
                    else:
                        new_columns[column_name] = column_type

        column_keys = new_columns.keys()
        column_types = new_columns.values()

        rows = []

        for table in tables:
            # Performance optimization for identical table structures
            if table.column_names == column_keys and table.column_types == column_types:
                rows.extend(table.rows)
            else:
                for row in table.rows:
                    data = []

                    for column_key in column_keys:
                        data.append(row.get(column_key, None))

                    rows.append(Row(data, column_keys))

        return Table(rows, column_keys, column_types, row_names=row_names, _is_fork=True)

    @allow_tableset_proxy
    def pivot(self, key=None, pivot=None, aggregation=None, computation=None, default_value=utils.default, key_name=None):
        """
        Pivot reorganizes the data in a table by grouping the data, aggregating
        those groups, optionally applying a computation, and then organizing
        the groups into new rows and columns.

        For example:

        +---------+---------+--------+
        |  name   |  race   | gender |
        +=========+=========+========+
        |  Joe    |  white  | male   |
        +---------+---------+--------+
        |  Jane   |  black  | female |
        +---------+---------+--------+
        |  Josh   |  black  | male   |
        +---------+---------+--------+
        |  Jim    |  asian  | female |
        +---------+---------+--------+

        This table can be pivoted with :code:`key` equal to "race" and
        :code:`pivot` equal to "gender". The default aggregation is
        :class:`.Count`. This would result in the following table.

        +---------+---------+--------+
        |  race   |  male   | female |
        +=========+=========+========+
        |  white  |  1      | 0      |
        +---------+---------+--------+
        |  black  |  1      | 1      |
        +---------+---------+--------+
        |  asian  |  0      | 1      |
        +---------+---------+--------+

        If one or more keys are specified then the resulting table will
        automatically have `row_names` set to those keys.

        See also the related method :meth:`Table.denormalize`.

        :param key:
            Either the name of a column from the this table to group by, a
            sequence of such column names, a :class:`function` that takes a
            row and returns a value to group by, or :code:`None`, in which case
            there will be only a single row in the output table.
        :param pivot:
            A column name whose unique values will become columns in the new
            table, or :code:`None` in which case there will be a single value
            column in the output table.
        :param aggregation:
            An instance of an :class:`.Aggregation` to perform on each group of
            data in the pivot table. (Each cell is the result of an aggregation
            of the grouped data.)

            If not specified this defaults to :class:`.Count` with no arguments.
        :param computation:
            An optional :class:`.Computation` instance to be applied to the
            aggregated sequence of values before they are transposed into the
            pivot table.

            Use the class name of the aggregation as your column name argument
            when constructing your computation. (This is "Count" if using the
            default value for :code:`aggregation`.)
        :param default_value:
            Value to be used for missing values in the pivot table. Defaults to
            :code:`Decimal(0)`. If performing non-mathematical aggregations you
            may wish to set this to :code:`None`.
        :param key_name:
            A name for the key column in the output table. This is most
            useful when the provided key is a function. This argument is not
            valid when :code:`key` is a sequence.
        :returns:
            A new :class:`Table`.
        """
        if key is None:
            key = []
        elif not utils.issequence(key):
            key = [key]
        elif key_name:
            raise ValueError('key_name is not a valid argument when key is a sequence.')

        if aggregation is None:
            aggregation = Count()

        groups = self

        for k in key:
            groups = groups.group_by(k, key_name=key_name)

        aggregation_name = six.text_type(aggregation)
        computation_name = six.text_type(computation) if computation else None

        def apply_computation(table):
            table = table.compute([
                (computation_name, computation)
            ])

            table = table.exclude([aggregation_name])

            return table

        if pivot is not None:
            groups = groups.group_by(pivot)

            column_type = aggregation.get_aggregate_data_type(groups)

            table = groups.aggregate([
                (aggregation_name, aggregation)
            ])

            pivot_count = len(set(table.columns[pivot].values()))

            if computation is not None:
                column_types = computation.get_computed_data_type(table)
                table = apply_computation(table)

            column_types = [column_type] * pivot_count

            table = table.denormalize(key, pivot, computation_name or aggregation_name, default_value=default_value, column_types=column_types)
        else:
            table = groups.aggregate([
                (aggregation_name, aggregation)
            ])

            if computation:
                table = apply_computation(table)

        return table

    @allow_tableset_proxy
    def normalize(self, key, properties, property_column='property', value_column='value', column_types=None):
        """
        Normalize a sequence of columns into two columns for field and value.

        For example:

        +---------+----------+--------+-------+
        |  name   | gender   | race   | age   |
        +=========+==========+========+=======+
        |  Jane   | female   | black  | 24    |
        +---------+----------+--------+-------+
        |  Jack   | male     | white  | 35    |
        +---------+----------+--------+-------+
        |  Joe    | male     | black  | 28    |
        +---------+----------+--------+-------+

        can be normalized on columns 'gender', 'race' and 'age':

        +---------+-----------+---------+
        |  name   | property  | value   |
        +=========+===========+=========+
        |  Jane   | gender    | female  |
        +---------+-----------+---------+
        |  Jane   | race      | black   |
        +---------+-----------+---------+
        |  Jane   | age       | 24      |
        +---------+-----------+---------+
        |  ...    |  ...      |  ...    |
        +---------+-----------+---------+

        This is the opposite of :meth:`Table.denormalize`.

        :param key:
            A column name or a sequence of column names that should be
            maintained as they are in the normalized table. Typically these
            are the tables unique identifiers and any metadata about them.
        :param properties:
            A column name or a sequence of column names that should be
            converted to properties in the new table.
        :param property_column:
            The name to use for the column containing the property names.
        :param value_column:
            The name to use for the column containing the property values.
        :param column_types:
            A sequence of two column types for the property and value column in
            that order or an instance of :class:`.TypeTester`. Defaults to a
            generic :class:`.TypeTester`.
        :returns:
            A new :class:`Table`.
        """
        new_rows = []

        if not utils.issequence(key):
            key = [key]

        if not utils.issequence(properties):
            properties = [properties]

        new_column_names = key + [property_column, value_column]

        row_names = []

        for row in self.rows:
            k = tuple(row[n] for n in key)
            left_row = list(k)

            if len(k) == 1:
                row_names.append(k[0])
            else:
                row_names.append(k)

            for f in properties:
                new_rows.append(Row(tuple(left_row + [f, row[f]]), new_column_names))

        key_column_types = [self.column_types[self.column_names.index(name)] for name in key]

        if column_types is None or isinstance(column_types, TypeTester):
            tester = TypeTester() if column_types is None else column_types
            force_update = dict(zip(key, key_column_types))
            force_update.update(tester._force)
            tester._force = force_update

            new_column_types = tester.run(new_rows, new_column_names)
        else:
            new_column_types = key_column_types + list(column_types)

        return Table(new_rows, new_column_names, new_column_types, row_names=row_names)

    @allow_tableset_proxy
    def denormalize(self, key=None, property_column='property', value_column='value', default_value=utils.default, column_types=None):
        """
        Denormalize a dataset so that unique values in a column become their
        own columns.

        For example:

        +---------+-----------+---------+
        |  name   | property  | value   |
        +=========+===========+=========+
        |  Jane   | gender    | female  |
        +---------+-----------+---------+
        |  Jane   | race      | black   |
        +---------+-----------+---------+
        |  Jane   | age       | 24      |
        +---------+-----------+---------+
        |  ...    |  ...      |  ...    |
        +---------+-----------+---------+

        Can be denormalized so that each unique value in `field` becomes a
        column with `value` used for its values.

        +---------+----------+--------+-------+
        |  name   | gender   | race   | age   |
        +=========+==========+========+=======+
        |  Jane   | female   | black  | 24    |
        +---------+----------+--------+-------+
        |  Jack   | male     | white  | 35    |
        +---------+----------+--------+-------+
        |  Joe    | male     | black  | 28    |
        +---------+----------+--------+-------+

        If one or more keys are specified then the resulting table will
        automatically have `row_names` set to those keys.

        This is the opposite of :meth:`Table.normalize`.

        :param key:
            A column name or a sequence of column names that should be
            maintained as they are in the normalized table. Typically these
            are the tables unique identifiers and any metadata about them. Or,
            :code:`None` if there are no key columns.
        :param field_column:
            The column whose values should become column names in the new table.
        :param property_column:
            The column whose values should become the values of the property
            columns in the new table.
        :param default_value:
            Value to be used for missing values in the pivot table. If not
            specified :code:`Decimal(0)` will be used for aggregations that
            return :class:`.Number` data and :code:`None` will be used for
            all others.
        :param column_types:
            A sequence of column types with length equal to number of unique
            values in field_column or an instance of :class:`.TypeTester`.
            Defaults to a generic :class:`.TypeTester`.
        :returns:
            A new :class:`Table`.
        """
        if key is None:
            key = []
        elif not utils.issequence(key):
            key = [key]

        field_names = []
        row_data = OrderedDict()

        for row in self.rows:
            row_key = tuple(row[k] for k in key)

            if row_key not in row_data:
                row_data[row_key] = OrderedDict()

            f = six.text_type(row[property_column])
            v = row[value_column]

            if f not in field_names:
                field_names.append(f)

            row_data[row_key][f] = v

        if default_value == utils.default:
            if isinstance(self.columns[value_column].data_type, Number):
                default_value = Decimal(0)
            else:
                default_value = None

        new_column_names = key + field_names

        new_rows = []
        row_names = []

        for k, v in row_data.items():
            row = list(k)

            if len(k) == 1:
                row_names.append(k[0])
            else:
                row_names.append(k)

            for f in field_names:
                if f in v:
                    row.append(v[f])
                else:
                    row.append(default_value)

            new_rows.append(Row(row, new_column_names))

        key_column_types = [self.column_types[self.column_names.index(name)] for name in key]

        if column_types is None or isinstance(column_types, TypeTester):
            tester = TypeTester() if column_types is None else column_types
            force_update = dict(zip(key, key_column_types))
            force_update.update(tester._force)
            tester._force = force_update

            new_column_types = tester.run(new_rows, new_column_names)
        else:
            new_column_types = key_column_types + list(column_types)

        return Table(new_rows, new_column_names, new_column_types, row_names=row_names)

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
            An instance of any subclass of :class:`.DataType`. If not provided
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
        # Infer bin start/end positions
        if start is None or end is None:
            start, end = utils.round_limits(
                Min(column_name).run(self),
                Max(column_name).run(self)
            )
        else:
            start = Decimal(start)
            end = Decimal(end)

        # Calculate bin size
        spread = abs(end - start)
        size = spread / count

        breaks = [start]

        # Calculate breakpoints
        for i in range(1, count + 1):
            top = start + (size * i)

            breaks.append(top)

        # Format bin names
        decimal_places = utils.max_precision(breaks)
        break_formatter = utils.make_number_formatter(decimal_places)

        def name_bin(i, j, first_exclusive=True, last_exclusive=False):
            inclusive = format_decimal(i, format=break_formatter)
            exclusive = format_decimal(j, format=break_formatter)

            output = u'[' if first_exclusive else u'('
            output += u'%s - %s' % (inclusive, exclusive)
            output += u']' if last_exclusive else u')'

            return output

        # Generate bins
        bin_names = []

        for i in range(1, len(breaks)):
            last_exclusive = (i == len(breaks) - 1)
            name = name_bin(breaks[i - 1], breaks[i], last_exclusive=last_exclusive)

            bin_names.append(name)

        bin_names.append(None)

        # Lambda method for actually assigning values to bins
        def binner(row):
            value = row[column_name]

            if value is None:
                return None

            i = 1

            try:
                while value >= breaks[i]:
                    i += 1
            except IndexError:
                i -= 1

            return bin_names[i - 1]

        # Pivot by lambda
        table = self.pivot(binner, key_name=column_name)

        # Sort by bin order
        return table.order_by(lambda r: bin_names.index(r[column_name]))

    def print_table(self, max_rows=None, max_columns=None, output=sys.stdout, max_column_width=20, locale=None):
        """
        Print a well-formatted preview of this table to the console or any
        other output.

        :param max_rows:
            The maximum number of rows to display before truncating the data.
        :param max_columns:
            The maximum number of columns to display before truncating the data.
        :param output:
            A file-like object to print to. Defaults to :code:`sys.stdout`.
        :param max_column_width:
            Truncate all columns to at most this width. The remainder will be
            replaced with ellipsis.
        :param locale:
            Provide a locale you would like to be used to format the output.
            By default it will use the system's setting.
        """
        print_table(self, max_rows, max_columns, output, max_column_width, locale)

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

    def print_bars(self, label_column_name='group', value_column_name='Count', domain=None, width=120, output=sys.stdout, printable=False):
        """
        Print a text-based bar chart of the columns names `label_column_name`
        and `value_column_name`.

        :param label_column_name:
            The column containing the label values. Defaults to "group", which
            is the default output of :meth:`Table.pivot` or :meth:`Table.bins`.
        :param value_column_name:
            The column containing the bar values. Defaults to "Count", which
            is the default output of :meth:`Table.pivot` or :meth:`Table.bins`.
        :param domain:
            A 2-tuple containing the minimum and maximum values for the chart's
            x-axis. The domain must be large enough to contain all values in
            the column.
        :param width:
            The width, in characters, to use for the bar chart. Defaults to
            `120`.
        :param output:
            A file-like object to print to. Defaults to :code:`sys.stdout`.
        :param printable:
            If true, only printable characters will be outputed.
        """
        print_bars(self, label_column_name, value_column_name, domain, width, output, printable)

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
