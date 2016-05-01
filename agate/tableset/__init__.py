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

import six
from six.moves import zip_longest

from agate.data_types import Text
from agate.mapped_sequence import MappedSequence
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
    :param _is_fork:
        Used internally to skip certain validation steps when data
        is propagated from an existing tablset.
    """
    def __init__(self, tables, keys, key_name='group', key_type=None, _is_fork=False):
        tables = tuple(tables)
        keys = tuple(keys)

        self._key_name = key_name
        self._key_type = key_type or Text()
        self._sample_table = tables[0]

        while isinstance(self._sample_table, TableSet):
            self._sample_table = self._sample_table[0]

        self._column_types = self._sample_table.column_types
        self._column_names = self._sample_table.column_names

        if not _is_fork:
            for table in tables:
                if any(not isinstance(a, type(b)) for a, b in zip_longest(table.column_types, self._column_types)):
                    raise ValueError('Not all tables have the same column types!')

                if table.column_names != self._column_names:
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

    def _fork(self, tables, keys, key_name=None, key_type=None):
        """
        Create a new :class:`.TableSet` using the metadata from this one.

        This method is used internally by functions like
        :meth:`.TableSet.having`.
        """
        if key_name is None:
            key_name = self._key_name

        if key_type is None:
            key_type = self._key_type

        return TableSet(tables, keys, key_name, key_type, _is_fork=True)


from agate.tableset.aggregate import aggregate
from agate.tableset.from_csv import from_csv
from agate.tableset.from_json import from_json
from agate.tableset.having import having
from agate.tableset.merge import merge
from agate.tableset.print_structure import print_structure
from agate.tableset.to_csv import to_csv
from agate.tableset.to_json import to_json

TableSet.aggregate = aggregate
TableSet.from_csv = from_csv
TableSet.from_json = from_json
TableSet.having = having
TableSet.merge = merge
TableSet.print_structure = print_structure
TableSet.to_csv = to_csv
TableSet.to_json = to_json
