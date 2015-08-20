#!/usr/bin/env python

from collections import Mapping, Sequence
from functools import wraps

try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

import six

from journalism.exceptions import ColumnDoesNotExistError, NullComputationError

#: String values which will be automatically cast to :code:`None`.
NULL_VALUES = ('', 'na', 'n/a', 'none', 'null', '.')

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

class ColumnMapping(Mapping):
    """
    Proxy access to :class:`Column` instances (for :class:`.Table`) or
    :class:`ColumnSet` instances (for :class:`.TableSet`).

    :param parent: The parent :class:`.Table` or :class:`.TableSet`.
    """
    def __init__(self, parent):
        self._parent = parent
        self._cached_len = None

    def __getitem__(self, k):
        try:
            i = self._parent._column_names.index(k)
        except ValueError:
            raise ColumnDoesNotExistError(k)

        return self._parent._get_column(i)

    def __iter__(self):
        return ColumnIterator(self._parent)

    def __len__(self):
        if self._cached_len is not None:
            return self._cached_len

        self._cached_len = len(self._parent._column_names)

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

class ColumnMethodProxy(object):
    """
    A proxy for :class:`ColumnSet` methods that converts them to individual
    calls on the ':class:`Column`'s of each :class:`Table` in the set.
    """
    def __init__(self, columnset, method_name):
        self.columnset = columnset
        self.method_name = method_name

    def __call__(self, *args, **kwargs):
        output = OrderedDict()

        for key, table in self.columnset._tableset.items():
            output[key] = getattr(table._get_column(self.columnset._index), self.method_name)(*args, **kwargs)

        return output

class ColumnSet(object):
    """
    A 'virtual' column that proxies :class:`.TableSet` column operations across
    all the identically named columns for each :class:`.Table` in the set.
    """
    def __init__(self, tableset, index):
        self._tableset = tableset
        self._index = index

        self.__unicode__ = ColumnMethodProxy(self, '__unicode__')
        self.__str__ = ColumnMethodProxy(self, '__str__')
        self.__getitem__ = ColumnMethodProxy(self, '__getitem__')
        self.__len__ = ColumnMethodProxy(self, '__len__')
        self.__eq__ = ColumnMethodProxy(self, '__eq__')
        self.__ne__ = ColumnMethodProxy(self, '__ne__')
        self.has_nulls = ColumnMethodProxy(self, 'has_nulls')
        self.any = ColumnMethodProxy(self, 'any')
        self.all = ColumnMethodProxy(self, 'all')
        self.count = ColumnMethodProxy(self, 'count')
        self.counts = ColumnMethodProxy(self, 'counts')

    def _proxy(self, method_name, *args, **kwargs):
        """
        Primary implementation of the method proxying. Returns a dict of
        results instead of a single value.
        """
        output = OrderedDict()

        for key, table in self._tableset.items():
            output[key] = getattr(table._get_column(self._index), method_name)(*args, **kwargs)

        return output

class ColumnIterator(six.Iterator):
    """
    Iterator over :class:`Column` instances (for :class:`.Table`) or
    :class:`ColumnSet` instances (for :class:`.TableSet`).

    :param parent: The parent :class:`.Table` or :class:`.TableSet`.
    """
    def __init__(self, parent):
        self._parent = parent
        self._i = 0

    def __next__(self):
        try:
            self._parent._column_names[self._i]
        except IndexError:
            raise StopIteration

        column = self._parent._get_column(self._i)

        self._i += 1

        return column

class ColumnType(object):
    """
    Base class for column data types.
    """
    def _create_column(self, table, index):
        raise NotImplementedError

    def _create_column_set(self, tableset, index):
        raise NotImplementedError
