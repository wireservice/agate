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

class ColumnType(object):
    """
    Base class for column data types.
    """
    def _create_column(self, table, index):
        raise NotImplementedError

    def _create_column_set(self, tableset, index):
        raise NotImplementedError

class ColumnMapping(Mapping):
    """
    Proxy access to :class:`Column` instances for :class:`.Table`.

    :param table: :class:`.Table`.
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

class ColumnIterator(six.Iterator):
    """
    Iterator over :class:`Column` instances within a :class:`.Table`.

    :param table: :class:`.Table`.
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

        self.has_nulls = HasNullsOperation(self)
        self.any = AnyOperation(self)
        self.all = AllOperation(self)
        self.count = CountOperation(self)

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

class ColumnOperation(object):
    """
    Base class defining an operation that can be performed on a column either
    to yield an individual value or as part of a :class:`.TableSet` aggregate.
    """
    def __init__(self, column):
        self._column = column

    def get_aggregate_column_type(self):
        raise NotImplementedError()

    def __call__(self):
        raise NotImplementedError()

class HasNullsOperation(ColumnOperation):
    """
    Returns :code:`True` if this column contains null values.
    """
    def get_aggregate_column_type(self):
        return BooleanType

    def __call__(self):
        return None in self._column._data()

class AnyOperation(ColumnOperation):
    """
    Returns :code:`True` if any value passes a truth test.

    :param test: A function that takes a value and returns :code:`True`
        or :code:`False`.
    """
    def get_aggregate_column_type(self):
        return BooleanType

    def __call__(self, test):
        return any(test(d) for d in self._column._data())

class AllOperation(ColumnOperation):
    """
    Returns :code:`True` if all values pass a truth test.

    :param test: A function that takes a value and returns :code:`True`
        or :code:`False`.
    """
    def get_aggregate_column_type(self):
        return BooleanType

    def __call__(self, test):
        return all(test(d) for d in self._column._data())

class CountOperation(ColumnOperation):
    """
    Count the number of times a specific value occurs in this column.

    :param value: The value to be counted.
    """
    def get_aggregate_column_type(self):
        return NumberType

    def __call__(self, value):
        count = 0

        for d in self._column._data():
            if d == value:
                count += 1

        return count
