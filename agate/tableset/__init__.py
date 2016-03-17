#!/usr/bin/env python

"""
The :class:`TableSet` class collects a set of related tables in a single data
structure. The most common way of creating a :class:`TableSet` is using the
:meth:`.Table.group_by` method, which is similar to SQL's ``GROUP BY`` keyword.
The resulting set of tables will all have identical columns structure.

:class:`TableSet` functions as a dictionary. Individual tables in the set can
be accessed by using their name as a key. If the table set was created using
:meth:`.Table.group_by` then the names of the tables will be the grouping
factors found in the original data.

:class:`TableSet` replicates the majority of the features of :class:`.Table`.
When methods such as :meth:`TableSet.select`, :meth:`TableSet.where` or
:meth:`TableSet.order_by` are used, the operation is applied to *each* table
in the set and the result is a new :class:`TableSet` instance made up of
entirely new :class:`.Table` instances.

:class:`TableSet` instances can also contain other TableSet's. This means you
can chain calls to :meth:`.Table.group_by` and :meth:`TableSet.group_by`
and end up with data grouped across multiple dimensions.
:meth:`TableSet.aggregate` on nested TableSets will then group across multiple
dimensions.
"""

from collections import OrderedDict
from glob import glob
import os
import json
import six
from six.moves import zip_longest
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

from agate.data_types import Text
from agate.mapped_sequence import MappedSequence
from agate.table import Table
from agate.table.print_structure import print_structure
from agate.utils import Patchable


class TableMethodProxy(object):
    """
    A proxy for :class:`TableSet` methods that converts them to individual
    calls on each :class:`.Table` in the set.
    """
    def __init__(self, tableset, method_name):
        self.tableset = tableset
        self.method_name = method_name

    def __call__(self, *args, **kwargs):
        tables = []

        for table in self.tableset:
            tables.append(getattr(table, self.method_name)(*args, **kwargs))

        return TableSet(
            tables,
            self.tableset.keys(),
            key_name=self.tableset.key_name,
            key_type=self.tableset.key_type
        )


class TableSet(MappedSequence, Patchable):
    """
    An group of named tables with identical column definitions. Supports
    (almost) all the same operations as :class:`.Table`. When executed on a
    :class:`TableSet`, any operation that would have returned a new
    :class:`.Table` instead returns a new :class:`TableSet`. Any operation
    that would have returned a single value instead returns a dictionary of
    values.

    TableSet is implemented as a subclass of :class:`.MappedSequence`

    :param tables:
        A sequence :class:`Table` instances.
    :param keys:
        A sequence of keys corresponding to the tables. These may be any type
        except :class:`int`.
    :param key_name:
        A name that describes the grouping properties. Used as the column
        header when the groups are aggregated. Defaults to the column name that
        was grouped on.
    :param key_type:
        An instance some subclass of :class:`.DataType`. If not provided it
        will default to a :class`.Text`.
    """
    def __init__(self, tables, keys, key_name='group', key_type=None):
        tables = tuple(tables)
        keys = tuple(keys)

        self._key_name = key_name
        self._key_type = key_type or Text()
        self._sample_table = tables[0]

        while isinstance(self._sample_table, TableSet):
            self._sample_table = self._sample_table[0]

        self._column_types = self._sample_table.column_types
        self._column_names = self._sample_table.column_names

        for table in tables:
            if any(not isinstance(a, type(b)) for a, b in zip_longest(table.column_types, self.column_types)):
                raise ValueError('Not all tables have the same column types!')

            if table.column_names != self.column_names:
                raise ValueError('Not all tables have the same column names!')

        MappedSequence.__init__(self, tables, keys)

    def __str__(self):
        """
        Print the tableset's structure via :meth:`TableSet.print_structure`.
        """
        structure = six.StringIO()

        self.print_structure(output=structure)

        return structure.getvalue()

    def __getattr__(self, name):
        """
        Proxy method access to :class:`Table` methods via instances of
        :class:`TableMethodProxy` that are created on-demand.
        """
        if name in self.__dict__:
            return self.__dict__[name]

        # Proxy table methods
        if name in Table.__dict__:
            if hasattr(Table.__dict__[name], 'allow_tableset_proxy'):
                return TableMethodProxy(self, name)
            else:
                raise AttributeError('Table method "%s" cannot be used as a TableSet method.' % name)

        raise AttributeError

    @property
    def key_name(self):
        """
        Get the name of the key this TableSet is grouped by. (If created using
        :meth:`.Table.group_by` then this is the original column name.)
        """
        return self._key_name

    @property
    def key_type(self):
        """
        Get the :class:`.DataType` this TableSet is grouped by. (If created
        using :meth:`.Table.group_by` then this is the original column type.)
        """
        return self._key_type

    @classmethod
    def from_csv(cls, dir_path, column_names=None, column_types=None, row_names=None, header=True, **kwargs):
        """
        Create a new :class:`TableSet` from a directory of CSVs.

        See :meth:`.Table.from_csv` for additional details.

        :param dir_path:
            Path to a directory full of CSV files. All CSV files in this
            directory will be loaded.
        :param column_names:
            See :meth:`Table.__init__`.
        :param column_types:
            See :meth:`Table.__init__`.
        :param row_names:
            See :meth:`Table.__init__`.
        :param header:
            See :meth:`Table.from_csv`.
        """
        if not os.path.isdir(dir_path):
            raise IOError('Specified path doesn\'t exist or isn\'t a directory.')

        tables = OrderedDict()

        for path in glob(os.path.join(dir_path, '*.csv')):
            name = os.path.split(path)[1].strip('.csv')

            tables[name] = Table.from_csv(path, column_names, column_types, row_names=row_names, header=header, **kwargs)

        return TableSet(tables.values(), tables.keys())

    def to_csv(self, dir_path, **kwargs):
        """
        Write each table in this set to a separate CSV in a given
        directory.

        See :meth:`.Table.to_csv` for additional details.

        :param dir_path:
            Path to the directory to write the CSV files to.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        for name, table in self.items():
            path = os.path.join(dir_path, '%s.csv' % name)

            table.to_csv(path, **kwargs)

    @classmethod
    def from_json(cls, path, column_names=None, column_types=None, keys=None, **kwargs):
        """
        Create a new :class:`TableSet` from a directory of JSON files or a
        single JSON object with key value (Table key and list of row objects)
        pairs for each :class:`Table`.

        See :meth:`.Table.from_json` for additional details.

        :param path:
            Path to a directory containing JSON files or filepath/file-like
            object of nested JSON file.
        :param keys:
            A list of keys of the top-level dictionaries for each file. If
            specified, length must be equal to number of JSON files in path.
        :param column_types:
            See :meth:`Table.__init__`.
        """
        if isinstance(path, six.string_types) and not os.path.isdir(path) and not os.path.isfile(path):
            raise IOError('Specified path doesn\'t exist.')

        tables = OrderedDict()

        if isinstance(path, six.string_types) and os.path.isdir(path):
            filepaths = glob(os.path.join(path, '*.json'))

            if keys is not None and len(keys) != len(filepaths):
                raise ValueError('If specified, keys must have length equal to number of JSON files')

            for i, filepath in enumerate(filepaths):
                name = os.path.split(filepath)[1].strip('.json')

                if keys is not None:
                    tables[name] = Table.from_json(filepath, keys[i], column_types=column_types, **kwargs)
                else:
                    tables[name] = Table.from_json(filepath, column_types=column_types, **kwargs)

        else:
            if hasattr(path, 'read'):
                js = json.load(path, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)
            else:
                with open(path, 'r') as f:
                    js = json.load(f, object_pairs_hook=OrderedDict, parse_float=Decimal, **kwargs)

            for key, value in js.items():
                tables[key] = Table.from_object(value, column_types=column_types, **kwargs)

        return TableSet(tables.values(), tables.keys())

    def to_json(self, path, nested=False, indent=None, **kwargs):
        """
        Write :class:`TableSet` to either a set of JSON files for each table or
        a single nested JSON file.

        See :meth:`.Table.to_json` for additional details.

        :param path:
            Path to the directory to write the JSON file(s) to. If nested is
            `True`, this should be a file path or file-like object to write to.
        :param nested:
            If `True`, the output will be a single nested JSON file with each
            Table's key paired with a list of row objects. Otherwise, the output
            will be a set of files for each table. Defaults to `False`.
        :param indent:
            See :meth:`Table.to_json`.
        """
        if not nested:
            if not os.path.exists(path):
                os.makedirs(path)

            for name, table in self.items():
                filepath = os.path.join(path, '%s.json' % name)

                table.to_json(filepath, indent=indent, **kwargs)
        else:
            close = True
            tableset_dict = OrderedDict()

            for name, table in self.items():
                output = StringIO()
                table.to_json(output, **kwargs)
                tableset_dict[name] = json.loads(output.getvalue(), object_pairs_hook=OrderedDict)

            if hasattr(path, 'write'):
                f = path
                close = False
            else:
                dirpath = os.path.dirname(path)

                if dirpath and not os.path.exists(dirpath):
                    os.makedirs(dirpath)

                f = open(path, 'w')

            json_kwargs = {'ensure_ascii': False, 'indent': indent}

            if six.PY2:
                json_kwargs['encoding'] = 'utf-8'

            json_kwargs.update(kwargs)
            json.dump(tableset_dict, f, json_kwargs)

            if close and f is not None:
                f.close()

    @property
    def column_types(self):
        """
        Get an ordered list of this :class:`.TableSet`'s column types.

        :returns:
            A :class:`tuple` of :class:`.DataType` instances.
        """
        return self._column_types

    @property
    def column_names(self):
        """
        Get an ordered list of this :class:`TableSet`'s column names.

        :returns:
            A :class:`tuple` of strings.
        """
        return self._column_names

    def print_structure(self, max_rows=20, output=sys.stdout):
        """
        Print the keys and row counts of each table in the tableset.

        :param max_rows:
            The maximum number of rows to display before truncating the data.
            Defaults to 20.
        :param output:
            The output used to print the structure of the :class:`Table`.
        :returns:
            None
        """
        max_length = min(len(self.items()), max_rows)

        left_column = self.keys()[0:max_length]
        right_column = [str(len(table.rows)) for key, table in self.items()[0:max_length]]
        column_headers = ['table_keys', 'row_count']

        print_structure(left_column, right_column, column_headers, output)

from agate.tableset.aggregate import aggregate
from agate.tableset.merge import merge

TableSet.aggregate = aggregate
TableSet.merge = merge
