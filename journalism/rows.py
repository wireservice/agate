#!/usr/bin/env python

from collections import Iterator, Mapping, Sequence

class RowIterator(Iterator):
    """
    Iterator over row proxies.
    """
    def __init__(self, table):
        self._table = table
        self._i = 0

    def next(self):
        try:
            self._table._data[self._i]
        except IndexError:
            raise StopIteration
        
        i = self._i
        self._i += 1

        return Row(self._table, i)

class RowSequence(Sequence):
    """
    Proxy access to rows by index.
    """
    def __init__(self, table):
        self._table = table

    def __getitem__(self, i):
        if isinstance(i, slice):
            indices = xrange(*i.indices(len(self)))

            return [Row(self._table, row) for row in indices]

        self._table._data[i]

        return Row(self._table, i)

    def __len__(self):
        return len(self._table._data)

class CellIterator(Iterator):
    """
    Iterator over row cells.
    """
    def __init__(self, row):
        self._row = row
        self._i = 0

    def next(self):
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

    def __getitem__(self, k):
        j = self._table._column_names.index(k)

        return self._table._data[self._i][j]

    def __len__(self):
        return len(self._table._data[self._i])

    def __iter__(self):
        return CellIterator(self)

    def __eq__(self, other):
        return self._table._data[self._i] == other
