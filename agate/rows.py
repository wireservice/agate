#!/usr/bin/env python

"""
This module contains agate's :class:`Row` implementation and various related
classes. In common usage nothing in this module should need to be instantiated
directly.
"""

from collections import Mapping, Sequence

import six

if six.PY3: #pragma: no cover
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
    def __init__(self, table, i):
        self._table = table
        self._i = i

    def __unicode__(self):
        data = self._table._data[self._i]

        sample = ', '.join(six.text_type(d) for d in data[:5])

        if len(data) > 5:
            sample = '%s, ...' % sample

        sample = '(%s)' % sample

        return '<agate.rows.Row: %s>' % sample

    def __str__(self):
        if six.PY2:
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())

    def __repr__(self):
        return str(self)

    def __getitem__(self, k):
        if isinstance(k, int):
            try:
                return self._table._data[self._i][k]
            except IndexError:
                raise ColumnDoesNotExistError(k)

        try:
            j = self._table._column_names.index(k)
        except ValueError:
            raise ColumnDoesNotExistError(k)

        return self._table._data[self._i][j]

    @memoize
    def __len__(self):
        return len(self._table._data[self._i])

    def __iter__(self):
        return CellIterator(self)

    def __eq__(self, other):
        return self._table._data[self._i] == other

class RowSequence(Sequence):
    """
    Proxy access to rows by index.

    :param table: The :class:`.Table` that contains the rows.
    """
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
    def __init__(self, table):
        self._table = table
        self._i = 0

    def __next__(self):
        try:
            row = self._table._get_row(self._i)
        except IndexError:
            raise StopIteration

        self._i += 1

        return row

class CellIterator(six.Iterator):
    """
    Iterator over row cells.

    :param row: The class:`Row` over which to iterate.
    """
    def __init__(self, row):
        self._row = row
        self._i = 0

    def __next__(self):
        try:
            v = self._row._table._data[self._row._i][self._i]
        except IndexError:
            raise StopIteration

        self._i += 1

        return v
