#!/usr/bin/env python

from collections import Iterator, Sequence

class RowIterator(Iterator):
    """
    Iterator over row proxies.
    """
    def __init__(self, table):
        self._table = table
        self._i = 0

    def next(self):
        # Ensure data exists
        self._table._data[self._i]
        
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
        self._table._data[i]

        return Row(self._table, i)

    def __len__(self):
        return len(self._table._data)

class Row(Sequence):
    """
    Proxy to row data.
    """
    def __init__(self, table, i):
        self._table = table
        self._i = i

    def __getitem__(self, j):
        return self._table._data[self._i][j]

    def __len__(self):
        return len(self._table._data[self._i])

    def __eq__(self, other):
        return list(self._table._data[self._i]) == other
