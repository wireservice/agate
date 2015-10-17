#!/usr/bin/env python

"""
This module contains agate's :class:`Row` implementation and various related
classes. In common usage nothing in this module should need to be instantiated
directly.
"""

from collections import Mapping, Sequence

import six

if six.PY3: #pragma: no cover
    #pylint: disable=W0622
    xrange = range

from agate.exceptions import ColumnDoesNotExistError, RowDoesNotExistError
from agate.utils import memoize

class Row(Mapping):
    """
    A row of data. Values within a row can be accessed by column name or column
    index.

    Row instances are immutable and may be shared between :class:`.Table`
    instances.

    :param column_names: The "keys" for this row.
    :param data: The "values" for this row.
    """
    #pylint: disable=W0212

    def __init__(self, column_names, data):
        self._column_names = column_names
        self._data = data

    def __unicode__(self):
        sample = u', '.join(repr(d) for d in self._data[:5])

        if len(self._data) > 5:
            sample = u'%s, ...' % sample

        return u'<agate.Row: (%s)>' % sample

    def __str__(self):
        if six.PY2:
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())

    def __getitem__(self, k):
        if isinstance(k, int):
            try:
                return self._data[k]
            except IndexError:
                raise ColumnDoesNotExistError(k)

        try:
            j = self._column_names.index(k)
        except ValueError:
            raise ColumnDoesNotExistError(k)

        return self._data[j]

    @memoize
    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return CellIterator(self)

    def __eq__(self, other):
        return self._data == other

class RowSequence(Sequence):
    """
    A sequence of :class:`Row` instances. Instances can be accessed by numeric
    index or row alias (if specified).

    :param rows: A sequence of :class:`Row` instances.
    :param row_alias: See :meth:`.Table.__init__`.
    """
    #pylint: disable=W0212

    def __init__(self, rows, row_alias=None):
        self._rows = rows
        self._has_row_alias = False
        self._alias_to_row = {}

        if row_alias:
            for i, row in enumerate(self._rows):
                alias_is_row_function = hasattr(row_alias, '__call__')

                if alias_is_row_function:
                    alias = row_alias(row)
                else:
                    alias = row[row_alias]

                # Prevent collisions between aliases and indices
                if isinstance(alias, int):
                    raise ValueError('Row aliases may not be of type int.')

                if alias in self._alias_to_row:
                    raise ValueError(u'Row alias was not unique: %s' % alias)

                self._alias_to_row[alias] = i

            self._has_row_alias = True

    def __getitem__(self, i):
        if isinstance(i, slice):
            indices = xrange(*i.indices(len(self)))

            return tuple(self._rows[row] for row in indices)
        elif isinstance(i, int):
            try:
                return self._rows[i]
            except IndexError:
                raise RowDoesNotExistError(i)
        else:
            try:
                return self._rows[self._alias_to_row[i]]
            except KeyError:
                raise RowDoesNotExistError(i)

    def __iter__(self):
        return RowIterator(self)

    @memoize
    def __len__(self):
        return len(self._rows)

class RowIterator(six.Iterator):
    """
    Iterator over :class:`Row` instances.

    :param row_sequence: The :class:`RowSequence` over which to iterate.
    """
    #pylint: disable=W0212

    def __init__(self, row_sequence):
        self._row_sequence = row_sequence
        self._index = 0

    def __next__(self):
        try:
            row = self._row_sequence[self._index]
        except RowDoesNotExistError:
            raise StopIteration

        self._index += 1

        return row

class CellIterator(six.Iterator):
    """
    Iterator over row cells.

    :param row: The class:`Row` over which to iterate.
    """
    #pylint: disable=W0212

    def __init__(self, row):
        self._row = row
        self._index = 0

    def __next__(self):
        try:
            v = self._row._data[self._index]
        except IndexError:
            raise StopIteration

        self._index += 1

        return v
