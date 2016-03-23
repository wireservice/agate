#!/usr/bin/env python

"""
The :class:`.Table` object is the most important class agate. Tables are
created by supplying row data, column names and subclasses of :class:`.DataType`
to the constructor. Once created, the data in a table **can not be changed**.
This concept is central to agate.

Instead of modifying the data, various methods can be used to create new,
derivative tables. For example, the :meth:`.Table.select` method creates a new
table with only the specified columns. The :meth:`.Table.where` method creates
a new table with only those rows that pass a test. And :meth:`.Table.order_by`
creates a sorted table. In all of these cases the output is new :class:`.Table`
and the existing table remains unmodified.

Tables are not themselves iterable, but the columns of the table can be
accessed via :attr:`.Table.columns` and the rows via :attr:`.Table.rows`. Both
sequences can be accessed either by numeric index or by name. (In the case of
rows, row names are optional.)
"""

import codecs
from collections import OrderedDict
import io
from itertools import chain
import json
import sys
import os.path
import warnings

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

import six
from six.moves import range, zip  # pylint: disable=W0622

from agate.columns import Column
from agate.data_types import DataType
from agate.mapped_sequence import MappedSequence
from agate.rows import Row
from agate.type_tester import TypeTester
from agate import utils
from agate.warns import warn_duplicate_column
from agate.utils import allow_tableset_proxy

if six.PY2:  # pragma: no cover
    from agate import csv_py2 as csv
else:
    from agate import csv_py3 as csv


@six.python_2_unicode_compatible
class Table(utils.Patchable):
    """
    A dataset consisting of rows and columns. Columns refer to "vertical" slices
    of data that must all be of the same type. Rows refer to "horizontal" slices
    of data that may (and usually do) contain mixed types.

    The sequence of :class:`.Column` instances are retrieved via the
    :attr:`.Table.columns` property. They may be accessed by either numeric
    index or by unique column name.

    The sequence of :class:`.Row` instances are retrieved via the
    :attr:`.Table.rows` property. They maybe be accessed by either numeric index
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
        be used. Alternatively, a dictionary with column names as keys and
        instances of :class:`.DataType` as values to specify some types.
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

        elif isinstance(column_types, dict):
            for v in six.itervalues(column_types):
                if not isinstance(v, DataType):
                    raise ValueError('Column types must be instances of DataType.')
            column_types = TypeTester(force=column_types)

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
            elif utils.issequence(row_names):
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
        Print the table's structure using :meth:`.Table.print_structure`.
        """
        structure = six.StringIO()

        self.print_structure(output=structure)

        return structure.getvalue()

    @property
    def column_types(self):
        """
        An tuple :class:`.DataType` instances.
        """
        return self._column_types

    @property
    def column_names(self):
        """
        An tuple of strings.
        """
        return self._column_names

    @property
    def row_names(self):
        """
        An tuple of strings, if this table has row names.

        If this table does not have row names, then :code:`None`.
        """
        return self._row_names

    @property
    def columns(self):
        """
        A :class:`.MappedSequence` with column names for keys and
        :class:`.Column` instances for values.
        """
        return self._columns

    @property
    def rows(self):
        """
        A :class:`.MappedSeqeuence` with row names for keys (if specified) and
        :class:`.Row` instances for values.
        """
        return self._rows

    def _fork(self, rows, column_names=None, column_types=None, row_names=None):
        """
        Create a new table using the metadata from this one.

        This method is used internally by functions like
        :meth:`.Table.order_by`.

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
        Create a copy of this table with different column names or row names.

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
    def from_csv(cls, path, column_names=None, column_types=None, row_names=None, skip_lines=0, header=True, sniff_limit=0, encoding='utf-8', **kwargs):
        """
        Create a new table from a CSV.

        This method uses agate's builtin CSV reader, which supplies encoding
        support for both Python 2 and Python 3.

        :code:`kwargs` will be passed through to the CSV reader.

        :param path:
            Filepath or file-like object from which to read CSV data.
        :param column_names:
            See :meth:`.Table.__init__`.
        :param column_types:
            See :meth:`.Table.__init__`.
        :param row_names:
            See :meth:`.Table.__init__`.
        :param skip_lines:
            Either a single number indicating the number of lines to skip from
            the top of the file or a sequence of line indexes to skip where the
            first line is index 0.
        :param header:
            If `True`, the first row of the CSV is assumed to contains headers
            and will be skipped. If `header` and `column_names` are both
            specified then a row will be skipped, but `column_names` will be
            used.
        :param sniff_limit:
            Limit CSV dialect sniffing to the specified number of bytes. Set to
            None to sniff the entire file. Defaults to 0 or no sniffing.
        :param encoding:
            Character encoding of the CSV file. Note: if passing in a file
            handle it is assumed you have already opened it with the correct
            encoding specified.
        """
        if hasattr(path, 'read'):
            lines = path.readlines()
        else:
            with io.open(path, encoding=encoding) as f:
                lines = f.readlines()

        if utils.issequence(skip_lines):
            lines = [line for i, line in enumerate(lines) if i not in skip_lines]
            contents = ''.join(lines)
        elif isinstance(skip_lines, int):
            contents = ''.join(lines[skip_lines:])
        else:
            raise ValueError('skip_lines argument must be an int or sequence')

        if sniff_limit is None:
            kwargs['dialect'] = csv.Sniffer().sniff(contents)
        elif sniff_limit > 0:
            kwargs['dialect'] = csv.Sniffer().sniff(contents[:sniff_limit])

        if six.PY2:
            contents = contents.encode('utf-8')

        rows = list(csv.reader(six.StringIO(contents), header=header, **kwargs))

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
        Create a new table from a JSON file.

        Once the JSON has been deseralized, the resulting Python object is
        passed to :meth:`.Table.from_object`.

        If the file contains a top-level dictionary you may specify what
        property contains the row list using the :code:`key` parameter.

        :code:`kwargs` will be passed through to :meth:`json.load`.

        :param path:
            Filepath or file-like object from which to read JSON data.
        :param row_names:
            See the :meth:`.Table.__init__`.
        :param key:
            The key of the top-level dictionary that contains a list of row
            arrays.
        :param newline:
            If `True` then the file will be parsed as "newline-delimited JSON".
        :param column_types:
            See :meth:`.Table.__init__`.
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
        Create a new table from a Python object.

        The object should be a list containing a dictionary for each "row".
        Nested objects or lists will also be parsed. For example, this object:

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

        Column names and types will be inferred from the data.

        Not all rows are required to have the same keys. Missing elements will
        be filled in with null values.

        :param obj:
            Filepath or file-like object from which to read JSON data.
        :param row_names:
            See :meth:`.Table.__init__`.
        :param column_types:
            See :meth:`.Table.__init__`.
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

        :code:`kwargs` will be passed through to the JSON encoder.

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
        Create a new table with only the specified columns.

        :param key:
            Either the name of a single column to include or a sequence of such
            names.
        :returns:
            A new :class:`.Table`.
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
        Create a new table without the specified columns.

        :param key:
            Either the name of a single column to exclude or a sequence of such
            names.
        :returns:
            A new :class:`.Table`.
        """
        if not utils.issequence(key):
            key = [key]

        selected_column_names = [n for n in self._column_names if n not in key]

        return self.select(selected_column_names)

    @allow_tableset_proxy
    def where(self, test):
        """
        Create a new table with only those rows that pass a test.

        :param test:
            A function that takes a :class:`.Row` and returns :code:`True` if
            it should be included.
        :type test:
            :class:`function`
        :returns:
            A new :class:`.Table`.
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
        Find the first row that passes test.

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
        Create a new table that is sorted.

        :param key:
            Either the name of a single column to sort by, a sequence of such
            names, or a :class:`function` that takes a row and returns a value
            to sort by.
        :param reverse:
            If `True` then sort in reverse (typically, descending) order.
        :returns:
            A new :class:`.Table`.
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
        Create a new table with fewer rows.

        See also: Python's builtin :func:`slice`.

        :param start_or_stop:
            If the only argument, then how many rows to include, otherwise,
            the index of the first row to include.
        :param stop:
            The index of the last row to include.
        :param step:
            The size of the jump between rows to include. (`step=2` will return
            every other row.)
        :returns:
            A new :class:`.Table`.
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
        Create a new table with only unique rows.

        :param key:
            Either the name of a single column to use to identify unique rows, a
            sequence of such column names, a :class:`function` that takes a
            row and returns a value to identify unique rows, or `None`, in
            which case the entire row will be checked for uniqueness.
        :returns:
            A new :class:`.Table`.
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

    def print_csv(self, **kwargs):
        """
        Print this table as a CSV.

        This is the same as passing :code:`sys.stdout` to :meth:`.Table.to_csv`.

        :code:`kwargs` will be passed on to :meth:`.Table.to_csv`.
        """
        self.to_csv(sys.stdout, **kwargs)

    def print_json(self, **kwargs):
        """
        Print this table as JSON.

        This is the same as passing :code:`sys.stdout` to
        :meth:`.Table.to_json`.

        :code:`kwargs` will be passed on to :meth:`.Table.to_json`.
        """
        self.to_json(sys.stdout, **kwargs)

    def print_structure(self, output=sys.stdout):
        """
        Print this table's column names and types.

        :param output:
            The output to print to.
        """
        from agate.table.print_structure import print_structure

        left_column = [n for n in self.column_names]
        right_column = [t.__class__.__name__ for t in self.column_types]
        column_headers = ['column_names', 'column_types']

        print_structure(left_column, right_column, column_headers, output)

from agate.table.aggregate import aggregate
from agate.table.bins import bins
from agate.table.compute import compute
from agate.table.denormalize import denormalize
from agate.table.group_by import group_by
from agate.table.homogenize import homogenize
from agate.table.join import join
from agate.table.merge import merge
from agate.table.normalize import normalize
from agate.table.pivot import pivot
from agate.table.print_bars import print_bars
from agate.table.print_html import print_html
from agate.table.print_table import print_table

Table.aggregate = aggregate
Table.bins = bins
Table.compute = compute
Table.denormalize = denormalize
Table.group_by = group_by
Table.homogenize = homogenize
Table.join = join
Table.merge = merge
Table.normalize = normalize
Table.pivot = pivot
Table.print_bars = print_bars
Table.print_html = print_html
Table.print_table = print_table
