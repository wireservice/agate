#!/usr/bin/env python

from collections import Mapping, Sequence, defaultdict
from decimal import Decimal, InvalidOperation
from functools import wraps

try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

import six

from journalism.exceptions import ColumnDoesNotExistError, NullComputationError, CastError

NULL_VALUES = ('', 'na', 'n/a', 'none', 'null', '.')
TRUE_VALUES = ('yes', 'y', 'true', 't')
FALSE_VALUES = ('no', 'n', 'false', 'f')

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
        try:
            i = self._table._column_names.index(k)
        except ValueError:
            raise ColumnDoesNotExistError(k)

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

def cast_text(d):
    """
    Cast a single value to a type appropriate for :class:`TextColumn`.
    """
    if d is None:
        return d

    if isinstance(d, six.string_types):
        d = d.strip()

        if d.lower() in NULL_VALUES:
            return None 

    return six.text_type(d)

def cast_boolean(d):
    if isinstance(d, bool) or d is None:
        return d

    if isinstance(d, six.string_types):
        d = d.replace(',' ,'').strip()

        d_lower = d.lower()

        if d_lower in NULL_VALUES:
            return None
        
        if d_lower in TRUE_VALUES:
            return True

        if d_lower in FALSE_VALUES:
            return False

    raise CastError('Can not convert value %s to bool for BooleanColumn.' % d) 

def cast_number(d):
    """
    Cast a single value to a type appropriate for :class:`NumberColumn`.
    """
    if isinstance(d, Decimal) or d is None:
        return d

    if isinstance(d, six.string_types):
        d = d.replace(',' ,'').strip()

        if d.lower() in NULL_VALUES:
            return None
    
    if isinstance(d, float):
        raise CastError('Can not convert float to Decimal for NumberColumn. Convert data to string first!')

    try:
        return Decimal(d)
    except InvalidOperation:
        raise CastError('Can not convert value "%s" to Decimal for NumberColumn.' % d) 

def median(data_sorted):
    """
    Compute the median value of this column.
    """
    length = len(data_sorted)

    if length % 2 == 1:
        return data_sorted[((length + 1) // 2) - 1]
    else:
        half = length // 2
        a = data_sorted[half - 1]
        b = data_sorted[half]

    return Decimal(a + b) / 2

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

    def __unicode__(self):
        data = self._data()

        sample = ', '.join(six.text_type(d) for d in data[:5])

        if len(data) > 5:
            sample = '%s, ...' % sample

        sample = '(%s)' % sample

        return '<journalism.columns.%s: %s>' % (self.__class__.__name__, sample)

    def __str__(self):
        return str(self.__unicode__())

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

    def _get_cast_func(self):
        """
        Return the function used to cast values in this column.
        """
        raise NotImplementedError   # pragma: no cover

    def _cast(self):
        """
        Cast values in this column to an appropriate type, if possible.
        """
        cast_func = self._get_cast_func()

        return tuple(cast_func(d) for d in self._data())

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
        one containing the values and a a second, :class:`NumberColumn`
        containing the counts.

        Resulting table will be sorted by descending count.
        """
        counts = OrderedDict()

        for d in self._data():
            if d not in counts:
                counts[d] = 0

            counts[d] += 1

        column_names = (self._table._column_names[self._index], 'count')
        column_types = (self._table._column_types[self._index], NumberColumn)
        data = (tuple(i) for i in counts.items())

        rows = sorted(data, key=lambda r: r[1], reverse=True)

        return self._table._fork(rows, column_types, column_names)

class TextColumn(Column):
    """
    A column containing unicode/string data.
    """
    def _get_cast_func(self):
        return cast_text 

    def max_length(self):
        return max([len(d) for d in self._data_without_nulls()])

class BooleanColumn(Column):
    """
    A column containing true/false data.
    """
    def _get_cast_func(self):
        return cast_boolean

    def any(self):
        """
        Returns True if any value passes a truth test.
        """
        return any(self._data())

    def all(self):
        """
        Returns True if all values pass a truth test.
        """
        return all(self._data())
  
class NumberColumn(Column):
    """
    A column containing numeric data.
    
    All data is represented by the :class:`decimal.Decimal` class.' 
    """
    def _get_cast_func(self):
        return cast_number

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
        return median(self._data_sorted())

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
        mean = self.mean()

        return sum((n - mean) ** 2 for n in data) / len(data)   

    @no_null_computations
    def stdev(self):
        """
        Compute the standard of deviation of this column.

        Will raise :exc:`.NullComputationError` if this column contains nulls.
        """
        return self.variance().sqrt()

    @no_null_computations
    def mad(self):
        """
        Compute the `median absolute deviation <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
        of this column.

        Will raise :exc:`.NullComputationError` if this column contains nulls.
        """
        data = self._data_sorted()
        m = median(data)

        return median(tuple(abs(n - m) for n in data))

