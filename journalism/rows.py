#!/usr/bin/env python

from collections import Mapping, Sequence

from journalism.exceptions import ColumnDoesNotExistError, RowDoesNotExistError
import six

if six.PY3:
    xrange = range

class RowIterator(six.Iterator):
    """
    Iterator over row proxies.
    """
    def __init__(self, table):
        self._table = table
        self._i = 0

    def __next__(self):
        try:
            self._table._data[self._i]
        except IndexError:
            raise StopIteration
        
        row = self._table._get_row(self._i)

        self._i += 1

        return row

class RowSequence(Sequence):
    """
    Proxy access to rows by index.
    """
    def __init__(self, table):
        self._table = table

    def __getitem__(self, i):
        if isinstance(i, slice):
            indices = xrange(*i.indices(len(self)))

            return tuple(self._table._get_row(row) for row in indices)

        # Verify the row exists
        try:
            self._table._data[i]
        except IndexError:
            raise RowDoesNotExistError(i)

        return self._table._get_row(i) 

    def __iter__(self):
        return RowIterator(self._table)

    def __len__(self):
        return len(self._table._data)

class CellIterator(six.Iterator):
    """
    Iterator over row cells.
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

class Row(Mapping):
    """
    Proxy to row data.
    """
    def __init__(self, table, i):
        self._table = table
        self._i = i

    def __repr__(self):
        data = self._table._data[self._i]

        sample = repr(data[:5])

        if len(data) > 5:
            last = sample[-1]
            sample = sample[:-1] + ', ...' + last

        return '<journalism.rows.Row: %s>' % sample 

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

    def __len__(self):
        return len(self._table._data[self._i])

    def __iter__(self):
        return CellIterator(self)

    def __eq__(self, other):
        return self._table._data[self._i] == other
