#!/usr/bin/env python

from collections import Mapping, Sequence, defaultdict
import datetime
from functools import wraps
import math

try:
    from cdecimal import Decimal, InvalidOperation
except ImportError: #pragma: no cover
    from decimal import Decimal, InvalidOperation

try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

from dateutil.parser import parse
import six

from journalism.exceptions import ColumnDoesNotExistError, NullComputationError, CastError

#: String values which will be automatically cast to :code:`None`.
NULL_VALUES = ('', 'na', 'n/a', 'none', 'null', '.')

#: String values which will be automatically cast to :code:`True`.
TRUE_VALUES = ('yes', 'y', 'true', 't')

#: String values which will be automatically cast to :code:`False`.
FALSE_VALUES = ('no', 'n', 'false', 'f')

def no_null_computations(func):
    """
    Function decorator that prevents illogical computations
    on columns containing nulls.
    """
    @wraps(func)
    def check(c, *args, **kwargs):
        if c.has_nulls():
            raise NullComputationError

        return func(c, *args, **kwargs)

    return check

def _median(data_sorted):
    """
    Compute the median value of a sequence of values.

    :param data_sorted: A sorted sequence of :class:`decimal.Decimal`.
    :returns: :class:`decimal.Decimal`.
    """
    length = len(data_sorted)

    if length % 2 == 1:
        return data_sorted[((length + 1) // 2) - 1]
    else:
        half = length // 2
        a = data_sorted[half - 1]
        b = data_sorted[half]

    return (a + b) / 2

class ColumnMapping(Mapping):
    """
    Proxy access to :class:`Column` instances by name.

    :param table: The :class:`.Table` containing the columns. 
    """
    def __init__(self, table):
        self._table = table
        self._cached_len = None

    def __getitem__(self, k):
        try:
            i = self._table._column_names.index(k)
        except ValueError:
            raise ColumnDoesNotExistError(k)

        return self._table._get_column(i) 

    def __iter__(self):
        return ColumnIterator(self._table)

    def __len__(self):
        if self._cached_len is not None:
            return self._cached_len

        self._cached_len = len(self._table._column_names)

        return self._cached_len 

class Column(Sequence):
    """
    Proxy access to column data. Instances of :class:`Column` should
    not be constructed directly. They are created by :class:`.Table`
    instances.

    :param table: The table that contains this column.
    :param index: The index of this column in the table.
    """
    def __init__(self, table, index):
        self._table = table
        self._index = index

        self._cached_data = None
        self._cached_data_without_nulls = None
        self._cached_data_sorted = None
        self._cached_len = None

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
        if self._cached_len is not None:
            return self._cached_len

        self._cached_len = len(self._data())

        return self._cached_len

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

    def has_nulls(self):
        """
        Returns True if this column contains null values.
        """
        return None in self._data()

    def any(self, test):
        """
        Returns :code:`True` if any value passes a truth test.
        
        :param test: A function that takes a value and returns :code:`True`
            or :code:`False`.
        """
        return any(test(d) for d in self._data())

    def all(self, test):
        """
        Returns :code:`True` if all values pass a truth test.
        
        :param test: A function that takes a value and returns :code:`True`
            or :code:`False`.
        """
        return all(test(d) for d in self._data())

    def count(self, value):
        """
        Count the number of times a specific value occurs in this column.

        :param value: The value to be counted.
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

        :returns: :class:`collections.OrderedDict` wth unique values
            as keys and counts as values.
        """
        counts = OrderedDict()

        for d in self._data():
            if d not in counts:
                counts[d] = 0

            counts[d] += 1

        return counts 

class ColumnType(object):
    """
    Base class for column data types.
    """
    def _create_column(self, table, index):
        raise NotImplementedError

class TextColumn(Column):
    """
    A column containing unicode/string data.
    """
    def max_length(self):
        return max([len(d) for d in self._data_without_nulls()])

class TextType(ColumnType):
    """
    Column type for :class:`TextColumn`.
    """
    def cast(self, d):
        """
        Cast a single value to :func:`unicode` (:func:`str` in Python 3).

        :param d: A value to cast.
        :returns: :func:`unicode` (:func:`str` in Python 3) or :code:`None`
        """
        if d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in NULL_VALUES:
                return None 

        return six.text_type(d)

    def _create_column(self, table, index):
        return TextColumn(table, index)

class BooleanColumn(Column):
    """
    A column containing :func:`bool` data.
    """
    def any(self):
        """
        Returns :code:`True` if any value is :code:`True`.
        """
        return any(self._data())

    def all(self):
        """
        Returns :code:`True` if all values are :code:`True`.
        """
        return all(self._data())

class BooleanType(ColumnType):
    """
    Column type for :class:`BooleanColumn`.
    """
    def cast(self, d):
        """
        Cast a single value to :func:`bool`.

        :param d: A value to cast.
        :returns: :func:`bool` or :code:`None`.
        """
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

    def _create_column(self, table, index):
        return BooleanColumn(table, index)

class NumberColumn(Column):
    """
    A column containing numeric data.
    
    All data is represented by the :class:`decimal.Decimal` class.' 
    """
    def sum(self):
        """
        Compute the sum of this column.

        :returns: :class:`decimal.Decimal`.
        """
        return sum(self._data_without_nulls())

    def min(self):
        """
        Compute the minimum value of this column.

        :returns: :class:`decimal.Decimal`.
        """
        return min(self._data_without_nulls())

    def max(self):
        """
        Compute the maximum value of this column.

        :returns: :class:`decimal.Decimal`.
        """
        return max(self._data_without_nulls())

    @no_null_computations
    def mean(self):
        """
        Compute the mean value of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        return self.sum() / len(self)

    @no_null_computations
    def median(self):
        """
        Compute the median value of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        return _median(self._data_sorted())

    @no_null_computations
    def mode(self):
        """
        Compute the mode value of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
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

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        data = self._data()
        mean = self.mean()

        return sum((n - mean) ** 2 for n in data) / len(data)   

    @no_null_computations
    def stdev(self):
        """
        Compute the standard of deviation of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        return self.variance().sqrt()

    @no_null_computations
    def mad(self):
        """
        Compute the `median absolute deviation <http://en.wikipedia.org/wiki/Median_absolute_deviation>`_
        of this column.

        :returns: :class:`decimal.Decimal`.
        :raises: :exc:`.NullComputationError`
        """
        data = self._data_sorted()
        m = _median(data)

        return _median(tuple(abs(n - m) for n in data))

    @no_null_computations
    def percentile(self, one_pct=None):
        """
        Compute the `percentile <http://stackoverflow.com/questions/2374640/how-do-i-calculate-percentiles-with-python-numpy/2753343#2753343>`_
        of this column or of one row.

        Returns a list of the percentiles.

        Will raise :exc:`.NullComputationError` if this column contains nulls.
        """
        data = self._data_sorted()

        if one_pct and one_pct % 1 != 0:
            raise ValueError('Percentile needs to be a whole number.')
        if one_pct and not 100 >= one_pct >= 1:
            raise ValueError('Percentile must be an integer less than or equal to 100 and greater than or equal to 1.')

        def percentiler(data, percent):
            if not data:
                return None

            i = Decimal(len(data) - 1) * percent

            if i % 1 == 0:
                return data[int(i)]

            f = i.quantize('0.0')
            c = f + 1 

            d0 = data[int(f)] * Decimal(c - i)
            d1 = data[int(c)] * Decimal(i - f)
            
            return d0 + d1

        if one_pct:
            return percentiler(data, Decimal(one_pct) * Decimal('.01'))
        else:
            percentile_list = []

            for each_pct in range(1, 101):
                percent = Decimal(each_pct) * Decimal('.01')
                percentile_list.append(percentiler(data, percent))
            
            return percentile_list

class NumberType(ColumnType):
    """
    Column type for :class:`NumberColumn`.
    """
    def cast(self, d):
        """
        Cast a single value to a :class:`decimal.Decimal`.

        :returns: :class:`decimal.Decimal` or :code:`None`.
        :raises: :exc:`.CastError`
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

    def _create_column(self, table, index):
        return NumberColumn(table, index)

class DateColumn(Column):
    """
    A column containing :func:`datetime.date` data.
    """
    def min(self):
        """
        Compute the earliest date in this column.

        :returns: :class:`datetime.date`.
        """
        return min(self._data_without_nulls())

    def max(self):
        """
        Compute the latest date in this column.

        :returns: :class:`datetime.date`.
        """
        return max(self._data_without_nulls())

class DateType(ColumnType):
    """
    Column type for :class:`DateColumn`.
    """
    def __init__(self, date_format=None):
        self.date_format = date_format

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.date`.

        :param date_format: An optional :func:`datetime.strptime`
            format string for parsing dates in this column.
        :returns: :class`datetime.date` or :code:`None`.
        :raises: :exc:`.CastError`
        """
        if isinstance(d, datetime.date) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in NULL_VALUES:
                return None

        if self.date_format:
            return datetime.datetime.strptime(d, self.date_format).date() 

        return parse(d).date()

    def _create_column(self, table, index):
        return DateColumn(table, index)

class DateTimeColumn(Column):
    """
    A column containing :func:`datetime.datetime` data.
    """
    def min(self):
        """
        Compute the earliest datetime in this column.

        :returns: :class:`datetime.datetime`.
        """
        return min(self._data_without_nulls())

    def max(self):
        """
        Compute the latest datetime in this column.

        :returns: :class:`datetime.datetime`.
        """
        return max(self._data_without_nulls())

class DateTimeType(ColumnType):
    """
    Column type for :class:`DateTimeColumn`.
    """
    def __init__(self, datetime_format=None):
        self.datetime_format = datetime_format

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.datetime`.

        :param date_format: An optional :func:`datetime.strptime`
            format string for parsing datetimes in this column.
        :returns: :class`datetime.datetime` or :code:`None`.
        :raises: :exc:`.CastError`
        """
        if isinstance(d, datetime.datetime) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in NULL_VALUES:
                return None

        if self.datetime_format:
            return datetime.datetime.strptime(d, self.datetime_format) 

        return parse(d)

    def _create_column(self, table, index):
        return DateTimeColumn(table, index)

class ColumnIterator(six.Iterator):
    """
    Iterator over :class:`Column` instances.

    :param table: The :class:`.Table` containing the columns.
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

