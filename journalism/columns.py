#!/usr/bin/env python

from collections import Iterator, Mapping, Sequence, defaultdict
from decimal import Decimal
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

    def any(self, func):
        """
        Returns True if any value passes a truth test.
        """
        return any([func(d) for d in self._data()])

    def all(self, func):
        """
        Returns True if all values pass a truth test.
        """
        return all([func(d) for d in self._data()])

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

    def count(self, value):
        """
        Count the number of times a specific value occurs in this column.
        """
        count = 0

        for d in self._data():
            if d == value:
                count += 1

        return count

    def counts(self):
        """
        Compute the number of instances of each unique value in this
        column.

        Returns a new :class:`journalism.table.Table`, with two columns,
        one containing the values and a a second, :class:`journalism.columns.IntColumn`
        containing the counts.

        Resulting table will be sorted by descending count.
        """
        i = self._table._column_names.index(self._k)
        
        counts = defaultdict(int)

        for d in self._data():
            counts[d] += 1

        column_names = [self._k, 'count']
        column_types = [self._table._column_types[i], IntColumn]
        data = [list(i) for i in counts.items()]

        rows = sorted(data, key=lambda r: r[1], reverse=True)

        return self._table._fork(rows, column_types, column_names)

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
        Compute the sum of this column.
        """
        return sum(self._data_without_nulls())

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
        return Decimal(self.sum()) / len(self)

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

        return (Decimal(a + b)) / 2

    @no_null_computations
    def mode(self):
        """
        Compute the mode value of this column.

        Will raise :exc:`journalism.exceptions.NullComputationError` if this column contains nulls.
        """
        data = self._data()
        state = defaultdict(int)

        for n in data:
            state[n] += 1

        return max(state.keys(), key=lambda x: state[x])

    @no_null_computations
    def variance(self):
        """
        Compute the variance of this column.

        Will raise :exc:`journalism.exceptions.NullComputationError` if this column contains nulls.
        """
        data = self._data()

        return sum((n - self.mean()) ** 2 for n in data) / len(data)   

    @no_null_computations
    def stdev(self):
        """
        Compute the standard of deviation of this column.

        Will raise :exc:`journalism.exceptions.NullComputationError` if this column contains nulls.
        """

        return self.variance().sqrt()

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

class DecimalColumn(NumberColumn):
    """
    A column containing decimal data.
    """
    def validate(self):
        """
        Verify all values in this column are Decimal or null.

        NB: We never use floats because of rounding error.

        Will raise :exc:`journalism.exceptions.ColumnValidationError`
        if validation fails.
        """
        for d in self._data():
            if not isinstance(d, Decimal) and d is not None:
                raise ColumnValidationError(d, self)

    def _cast(self):
        """
        Cast values in this column to Decimal.

        NB: casting from float will introduce precision
        errors. Always cast from string, e.g. '3.14'.
        """
        casted = []

        for d in self._data():
            if isinstance(d, basestring):
                d = d.replace(',' ,'').strip()

            if d == '' or d is None:
                casted.append(None)
            else:
                casted.append(Decimal(d))

        return casted

