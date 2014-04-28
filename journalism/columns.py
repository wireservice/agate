#!/usr/bin/env python

from collections import Mapping, Sequence, defaultdict
from decimal import Decimal
from functools import wraps

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import six

from journalism.exceptions import ColumnDoesNotExistError, ColumnValidationError, NullComputationError

class ColumnIterator(six.Iterator):
    """
    Iterator over :class:`Column` instances.
    """
    def __init__(self, table):
        self._table = table
        self._i = 0

    def __next__(self):
        try:
            self._table._column_names[self._i]
        except IndexError:
            raise StopIteration

        column = self._table._get_column(self._i)

        self._i += 1

        return column 

class ColumnMapping(Mapping):
    """
    Proxy access to :class:`Column` instances by name.
    """
    def __init__(self, table):
        self._table = table

    def __getitem__(self, k):
        if k not in self._table._column_names:
            raise ColumnDoesNotExistError(k)

        i = self._table._column_names.index(k)

        return self._table._get_column(i) 

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
    def check(c, *args, **kwargs):
        if c.has_nulls():
            raise NullComputationError

        return func(c)

    return check

class Column(Sequence):
    """
    Proxy access to column data.
    """
    def __init__(self, table, index):
        self._table = table
        self._index = index

        self._cached_data = None
        self._cached_data_without_nulls = None
        self._cached_data_sorted = None

    def __repr__(self):
        data = self._data()

        sample = repr(data[:5])

        if len(data) > 5:
            last = sample[-1]
            sample = sample[:-1] + ', ...' + last

        return '<journalism.columns.%s: %s>' % (self.__class__.__name__, sample)

    def _data(self):
        if self._cached_data is None:
            self._cached_data = tuple(r[self._index] for r in self._table._data)

        return self._cached_data

    def _data_without_nulls(self):
        if self._cached_data_without_nulls is None:
            self._cached_data_without_nulls = tuple(d for d in self._data() if d is not None)

        return self._cached_data_without_nulls

    def _data_sorted(self):
        if self._cached_data_sorted is None:
            self._cached_data_sorted = sorted(self._data())

        return self._cached_data_sorted

    def __getitem__(self, j):
        return self._data()[j]

    def __len__(self):
        return len(self._data())

    def __eq__(self, other):
        """
        Ensure equality test with lists works.
        """
        return self._data() == other

    def __ne__(self, other):
        """
        Ensure inequality test with lists works.
        """
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
        return any(func(d) for d in self._data())

    def all(self, func):
        """
        Returns True if all values pass a truth test.
        """
        return all(func(d) for d in self._data())

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

        Returns a new :class:`.Table`, with two columns,
        one containing the values and a a second, :class:`IntColumn`
        containing the counts.

        Resulting table will be sorted by descending count.
        """
        counts = OrderedDict()

        for d in self._data():
            if d not in counts:
                counts[d] = 0

            counts[d] += 1

        column_names = (self._table._column_names[self._index], 'count')
        column_types = (self._table._column_types[self._index], IntColumn)
        data = (tuple(i) for i in counts.items())

        rows = sorted(data, key=lambda r: r[1], reverse=True)

        return self._table._fork(rows, column_types, column_names)

class TextColumn(Column):
    """
    A column containing unicode/string data.
    """
    def validate(self):
        """
        Verify all values in this column are string/unicode or null.

        Will raise :exc:`.ColumnValidationError`
        if validation fails.
        """
        for d in self._data():
            if not isinstance(d, six.string_types) and d is not None:
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
                casted.append(six.u(d))

        return casted

class NumberColumn(Column):
    """
    A column containing numeric data.

    Base class for :class:`IntColumn` and :class:`DecimalColumn`.
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

        Will raise :exc:`.NullComputationError` if this column contains nulls.
        """
        return Decimal(self.sum()) / len(self)

    @no_null_computations
    def median(self):
        """
        Compute the median value of this column.

        Will raise :exc:`.NullComputationError` if this column contains nulls.
        """
        data = self._data_sorted()
        length = len(data)

        if length % 2 == 1:
            return data[((length + 1) / 2) - 1]
        else:
            half = length // 2
            a = data[half - 1]
            b = data[half]

        return Decimal(a + b) / 2

    @no_null_computations
    def mode(self):
        """
        Compute the mode value of this column.

        Will raise :exc:`.NullComputationError` if this column contains nulls.
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

        Will raise :exc:`.NullComputationError` if this column contains nulls.
        """
        data = self._data()

        return sum((n - self.mean()) ** 2 for n in data) / len(data)   

    @no_null_computations
    def stdev(self):
        """
        Compute the standard of deviation of this column.

        Will raise :exc:`.NullComputationError` if this column contains nulls.
        """

        return self.variance().sqrt()

class IntColumn(NumberColumn):
    """
    A column containing integer data.
    """
    def validate(self):
        """
        Verify all values in this column are int or null.

        Will raise :exc:`.ColumnValidationError` if validation fails.
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
            if isinstance(d, six.string_types):
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

        Will raise :exc:`.ColumnValidationError` if validation fails.
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
            if isinstance(d, six.string_types):
                d = d.replace(',' ,'').strip()

            if d == '' or d is None:
                casted.append(None)
            else:
                casted.append(Decimal(d))

        return casted

