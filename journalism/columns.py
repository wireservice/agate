#!/usr/bin/env python

from collections import Iterator, Mapping, Sequence
import copy
from functools import wraps
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
    @wraps(func)
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
        """
        Verify values in this column are of an appopriate type.
        """
        raise NotImplementedError

    def _cast(self):
        """
        Cast values in this column to an appropriate type, if possible.
        """
        raise NotImplementedError

    def has_nulls(self):
        """
        Returns True if this column contains null values.
        """
        return None in self._data()

    def map(self, func, new_column_type=None, new_column_name=None):
        """
        Apply an arbitrary function to a column of data and
        optionally change it's type and/or name.

        Returns a new :class:`journalism.table.Table`.
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
    """
    A column containing unicode/string data.
    """
    def validate(self):
        """
        Verify all values in this column are string/unicode or null.

        Will raise :exc:`journalism.exceptions.ColumnValidationError`
        if validation fails.
        """
        for d in self._data():
            if not isinstance(d, basestring) and d is not None:
                raise ColumnValidationError(d, self)

    def _cast(self):
        """
        Cast values to unicode.
        """
        casted = []

        for d in self._data():
            if d == '':
                casted.append(None)
            else:
                casted.append(unicode(d))

        return casted

class NumberColumn(Column):
    """
    A column containing numeric data.
    
    Base class for :class:`IntColumn` and :class:`FloatColumn`.
    """
    def sum(self):
        """
        Implemented in subclasses to take advantage of floating
        point precision.
        """
        raise NotImplementedError

    def min(self):
        """
        Compute the minimum value of this column.
        """
        return min(self._data_without_nulls())

    def max(self):
        """
        Compute the maximum value of this column.
        """
        return max(self._data_without_nulls())

    @no_null_computations
    def mean(self):
        """
        Compute the mean value of this column.

        Will raise :exc:`journalism.exceptions.NullComputationError` if this column contains nulls.
        """
        return float(self.sum() / len(self))

    @no_null_computations
    def median(self):
        """
        Compute the median value of this column.

        Will raise :exc:`journalism.exceptions.NullComputationError` if this column contains nulls.
        """
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
        """
        TODO: Compute the mode of this column.

        Will raise :exc:`journalism.exceptions.NullComputationError` if this column contains nulls.
        """
        raise NotImplementedError

    @no_null_computations
    def stdev(self):
        """
        Compute the standard of deviation of this column.

        Will raise :exc:`journalism.exceptions.NullComputationError` if this column contains nulls.
        """
        data = self._data()

        return math.sqrt(sum(math.pow(v - self.mean(), 2) for v in data) / len(data))

class IntColumn(NumberColumn):
    """
    A column containing integer data.
    """
    def validate(self):
        """
        Verify all values in this column are int or null.

        Will raise :exc:`journalism.exceptions.ColumnValidationError`
        if validation fails.
        """
        for d in self._data():
            if not isinstance(d, int) and d is not None:
                raise ColumnValidationError(d, self)

    def _cast(self):
        """
        Cast values in this column to integer.
        """
        casted = []

        for d in self._data():
            if isinstance(d, basestring):
                d = d.replace(',' ,'').strip()

            if d == '' or d is None:
                casted.append(None)
            else:
                casted.append(int(d))

        return casted

    def sum(self):
        """
        Compute the sum of this column.
        """
        return sum(self._data_without_nulls())

class FloatColumn(NumberColumn):
    """
    A column containing float data.
    """
    def validate(self):
        """
        Verify all values in this column are float or null.

        Will raise :exc:`journalism.exceptions.ColumnValidationError`
        if validation fails.
        """
        for d in self._data():
            if not isinstance(d, float) and d is not None:
                raise ColumnValidationError(d, self)

    def _cast(self):
        """
        Cast values in this column to float.
        """
        casted = []

        for d in self._data():
            if isinstance(d, basestring):
                d = d.replace(',' ,'').strip()

            if d == '' or d is None:
                casted.append(None)
            else:
                casted.append(float(d))

        return casted

    def sum(self):
        """
        Compute the sum of this column using :func:`math.fsum` for precision.
        """
        return math.fsum(self._data_without_nulls())

