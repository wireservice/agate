#!/usr/bin/env python

from collections import Iterator, Mapping, Sequence
import copy
import math

from journalism.exceptions import ColumnValidationError, NullComputationError

class ColumnIterator(Iterator):
    """
    Iterator over column proxies.
    """
    def __init__(self, table):
        self._table = table
        self._i = 0

    def next(self):
        try:
            v = self._table._column_names[self._i]
        except IndexError:
            raise StopIteration

        column_type = self._table._column_types[self._i]

        self._i += 1
        
        return column_type(self._table, v)

class ColumnMapping(Mapping):
    """
    Proxy access to columns by name.
    """
    def __init__(self, table):
        self._table = table

    def __getitem__(self, k):
        if k not in self._table._column_names:
            raise KeyError

        i = self._table._column_names.index(k)
        column_type = self._table._column_types[i]

        return column_type(self._table, k)

    def __iter__(self):
        return ColumnIterator(self._table)

    def __len__(self):
        return len(self._table._column_names)

def no_null_computations(func):
    """
    Function decorator that prevents illogical computations
    on columns containing nulls.
    """
    def check(l, *args, **kwargs):
        if l.has_nulls():
            raise NullComputationError

        return func(l)

    return check

class Column(Sequence):
    """
    Proxy access to column data.
    """
    def __init__(self, table, k):
        self._table = table
        self._k = k

    def _data(self):
        # TODO: memoize?
        i = self._table._column_names.index(self._k)

        return [r[i] for r in self._table._data]

    def _data_without_nulls(self):
        # TODO: memoize?
        return [d for d in self._data() if d is not None]

    def _data_sorted(self):
        # TODO: memoize?
        return sorted(self._data())

    def __getitem__(self, j):
        return self._data()[j]

    def __len__(self):
        return len(self._data()) 

    def __eq__(self, other):
        return self._data() == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def validate(self):
        raise NotImplementedError

    def has_nulls(self):
        return None in self._data()

    def apply(self, func, new_column_type=None, new_column_name=None):
        """
        Apply an arbitrary function to a column of data and
        optionally change it's type and/or name.

        Returns a new Table.
        """
        i = self._table._column_names.index(self._k)
        
        data = copy.deepcopy(self._table._data)
        column_types = copy.deepcopy(self._table._column_types)
        column_names = copy.deepcopy(self._table._column_names)

        for row in data:
            row[i] = func(row[i])

        if new_column_type:
            column_types[i] = new_column_type

        if new_column_name:
            column_names[i] = new_column_name

        return self._table._fork(data, column_types, column_names) 

class TextColumn(Column):
    def validate(self):
        for d in self._data():
            if not isinstance(d, basestring) and d is not None:
                raise ColumnValidationError

class NumberColumn(Column):
    def sum(self):
        """
        Implemented in subclasses to take advantage of floating
        point precision.
        """
        raise NotImplementedError

    def min(self):
        return min(self._data_without_nulls())

    def max(self):
        return max(self._data_without_nulls())

    @no_null_computations
    def mean(self):
        return float(self.sum() / len(self))

    @no_null_computations
    def median(self):
        data = self._data_sorted()
        length = len(data)

        if length % 2 == 1:
            return data[((length + 1) / 2) - 1]
        else:
            a = data[(length / 2) - 1]
            b = data[length / 2]

        return (float(a + b)) / 2  

    @no_null_computations
    def mode(self):
        # TODO
        raise NotImplementedError

    @no_null_computations
    def stdev(self):
        data = self._data()

        return math.sqrt(sum(math.pow(v - self.mean(), 2) for v in data) / len(data))

class IntColumn(NumberColumn):
    def validate(self):
        for d in self._data():
            if not isinstance(d, int) and d is not None:
                raise ColumnValidationError

    def sum(self):
        return sum(self._data_without_nulls())

class FloatColumn(NumberColumn):
    def validate(self):
        for d in self._data():
            if not isinstance(d, float) and d is not None:
                raise ColumnValidationError

    def sum(self):
        return math.fsum(self._data_without_nulls())

