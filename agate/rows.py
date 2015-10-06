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
    Proxy to row data.

    Values within a row can be accessed by column name or
    column index.

    :param table: The :class:`Table` that contains this row.
    :param i: The index of this row in the :class:`Table`.
    """
    #pylint: disable=W0212

    def __init__(self, table, index):
        self._table = table
        self._index = index

    def __unicode__(self):
        data = self._table._data[self._index]

        sample = u', '.join(repr(d) for d in data[:5])

        if len(data) > 5:
            sample = u'%s, ...' % sample

        return u'<agate.Row: (%s)>' % sample

    def __str__(self):
        if six.PY2:
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())

    def __repr__(self):
        return u'<agate.Row: index=%i>' % self._index

    def __getitem__(self, k):
        if isinstance(k, int):
            try:
                return self._table._data[self._index][k]
            except IndexError:
                raise ColumnDoesNotExistError(k)

        try:
            j = self._table._column_names.index(k)
        except ValueError:
            raise ColumnDoesNotExistError(k)

        return self._table._data[self._index][j]

    @memoize
    def __len__(self):
        return len(self._table._data[self._index])

    def __iter__(self):
        return CellIterator(self)

    def __eq__(self, other):
        return self._table._data[self._index] == other

    @property
    def index(self):
        return self._index

class RowSequence(Sequence):
    """
    Proxy access to rows by index.

    :param table: The :class:`.Table` that contains the rows.
    """
    #pylint: disable=W0212

    def __init__(self, table):
        self._table = table

    def __getitem__(self, i):
        if isinstance(i, slice):
            indices = xrange(*i.indices(len(self)))

            return tuple(self._table._get_row(row) for row in indices)

        try:
            return self._table._get_row(i)
        except IndexError:
            raise RowDoesNotExistError(i)

    def __iter__(self):
        return RowIterator(self._table)

    @memoize
    def __len__(self):
        return self._table._get_row_count()

class RowIterator(six.Iterator):
    """
    Iterator over row proxies.

    :param table: The :class:`.Table` of which to iterate.
    """
    #pylint: disable=W0212

    def __init__(self, table):
        self._table = table
        self._index = 0

    def __next__(self):
        try:
            row = self._table._get_row(self._index)
        except IndexError:
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
            v = self._row._table._data[self._row.index][self._index]
        except IndexError:
            raise StopIteration

        self._index += 1

        return v
