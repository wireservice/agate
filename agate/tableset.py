#!/usr/bin/env python

"""
This module contains the :class:`TableSet` class which abstracts an set of
related tables into a single data structure. The most common way of creating a
:class:`TableSet` is using the :meth:`.Table.group_by` method, which is
similar to SQL's ``GROUP BY`` keyword. The resulting set of tables each have
identical columns structure.

:class:`TableSet` functions as a dictionary. Individual tables in the set can
be accessed by using their name as a key. If the table set was created using
:meth:`.Table.group_by` then the names of the tables will be the group factors
found in the original data.

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

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from agate.data_types import Text
from agate.mapped_sequence import MappedSequence
from agate.rows import Row
from agate.table import Table
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
            if any(not isinstance(a, type(b)) for a,b in zip_longest(table.column_types, self.column_types)):
                raise ValueError('Not all tables have the same column types!')

            if table.column_names != self.column_names:
                raise ValueError('Not all tables have the same column names!')

        MappedSequence.__init__(self, tables, keys)

    def __getattr__(self, name):
        """
        Proxy method access to :class:`Table` methods via instances of
        :class:`TableMethodProxy` that are created on-demand.
        """
        if name in self.__dict__:
            return self.__dict__[name]

        # Proxy table methods
        if name in Table.__dict__:
            if Table.__dict__[name].allow_tableset_proxy:
                return TableMethodProxy(self, name)

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
            tableset_dict = {}
            for name, table in self.items():
                output = StringIO()
                table.to_json(output, **kwargs)
                tableset_dict[name] = json.loads(output.getvalue())
                
            if hasattr(path, 'write'):
                f = path
                close = False
            else:
                dirpath = os.path.dirname(path)
                
                if dirpath and not os.path.exists(dirpath):
                    os.makedirs(dirpath)

                f = open(path, 'w')
            
            json_kwargs = { 'ensure_ascii': False, 'indent': indent }

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

    def merge(self):
        """
        Convert this TableSet into a single table. This is the inverse of
        :meth:`.Table.group_by`.

        Any `row_names` set on the merged tables will be lost in this
        process.

        :returns:
            A new :class:`Table`.
        """
        column_names = list(self.column_names)
        column_types = list(self.column_types)

        column_names.insert(0, self.key_name)
        column_types.insert(0, self.key_type)

        rows = []

        for key, table in self.items():
            for row in table.rows:
                rows.append(Row((key,) + tuple(row), column_names))

        return Table(rows, column_names, column_types)

    def _aggregate(self, aggregations=[]):
        """
        Recursive aggregation allowing for TableSet's to be nested inside
        one another.

        See :meth:`TableSet.aggregate` for the user-facing API.
        """
        output = []

        # Process nested TableSet's
        if isinstance(self._values[0], TableSet):
            for key, tableset in self.items():
                column_names, column_types, nested_output, row_name_columns = tableset._aggregate(aggregations)

                for row in nested_output:
                    row.insert(0, key)

                    output.append(row)

            column_names.insert(0, self._key_name)
            column_types.insert(0, self._key_type)
            row_name_columns.insert(0, self._key_name)
        # Regular Tables
        else:
            column_names = [self._key_name]
            column_types = [self._key_type]
            row_name_columns = [self._key_name]

            for new_column_name, aggregation in aggregations:
                column_names.append(new_column_name)
                column_types.append(aggregation.get_aggregate_data_type(self._sample_table))

            for name, table in self.items():
                for new_column_name, aggregation in aggregations:
                    aggregation.validate(table)

            for name, table in self.items():
                new_row = [name]

                for new_column_name, aggregation in aggregations:
                    new_row.append(aggregation.run(table))

                output.append(new_row)

        return column_names, column_types, output, row_name_columns

    def aggregate(self, aggregations=[]):
        """
        Aggregate data from the tables in this set by performing some
        set of column operations on the groups and coalescing the results into
        a new :class:`.Table`.

        :code:`aggregations` must be a sequence of tuples, where each has two
        parts: a :code:`new_column_name` and a :class:`.Aggregation` instance.

        The resulting table will have the keys from this :class:`TableSet` (and
        any nested TableSets) set as its :code:`row_names`. See
        :meth:`.Table.__init__` for more details.

        :param aggregations:
            A list of tuples in the format
            :code:`(new_column_name, aggregation)`.
        :returns:
            A new :class:`.Table`.
        """
        column_names, column_types, output, row_name_columns = self._aggregate(aggregations)

        if len(row_name_columns) == 1:
            row_names = row_name_columns[0]
        else:
            row_names = lambda r: tuple(r[n] for n in row_name_columns)

        return Table(output, column_names, column_types, row_names=row_names)
