#!/usr/bin/env python

from collections import Iterator, Mapping

class ColumnIterator(Iterator):
    def __init__(self, table):
        self._table = table
        self._i = 0

    def next(self):
        v = self._table._column_names[self._i]
        self._i += 1

        return ColumnContext(self._table, v)

class ColumnProxy(Mapping):
    def __init__(self, table):
        self._table = table

    def __getitem__(self, k):
        self._table.column_names[k] 

        return ColumnContext(self._table, k)

    def __iter__(self):
        return ColumnIterator(self._table)

    def __len__(self):
        pass

class ColumnContext(object):
    def __init__(self, table, k):
        self._table = table
        self.k = k

class Column(object):
    pass

class TextColumn(Column):
    pass

class IntColumn(Column):
    pass

class FloatColumn(Column):
    pass
