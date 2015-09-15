#!/usr/bin/env python

from collections import Mapping, Sequence

try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

import six

from agate.exceptions import ColumnDoesNotExistError
from agate.utils import NullOrder, memoize

class Column(Sequence):
    """
    Proxy access to column data. Instances of :class:`Column` should
    not be constructed directly. They are created by :class:`.Table`
    instances.

    :param table: The table that contains this column.
    :param index: The index of this column in the table.
    """
    def __init__(self, data_type, table, index):
        self._data_type = data_type
        self._table = table
        self._index = index

        self._aggregate_cache = {}

    def __unicode__(self):
        data = self.get_data()

        sample = ', '.join(six.text_type(d) for d in data[:5])

        if len(data) > 5:
            sample = '%s, ...' % sample

        sample = '(%s)' % sample

        return '<agate.columns.%s: %s>' % (self.__class__.__name__, sample)

    def __str__(self):
        if six.PY2:
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())  #pragma: no cover

    def __getitem__(self, j):
        return self.get_data()[j]

    @memoize
    def __len__(self):
        return len(self.get_data())

    def __eq__(self, other):
        """
        Ensure equality test with lists works.
        """
        return self.get_data() == other

    def __ne__(self, other):
        """
        Ensure inequality test with lists works.
        """
        return not self.__eq__(other)

    @property
    def data_type(self):
        return self._data_type

    @memoize
    def get_data(self):
        """
        Get the data contained in this column as a :class:`tuple`.
        """
        return tuple(r[self._index] for r in self._table._data)

    @memoize
    def get_data_without_nulls(self):
        """
        Get the data contained in this column with any null values removed.
        """
        return tuple(d for d in self.get_data() if d is not None)

    def _null_handler(self, k):
        """
        Key method for sorting nulls correctly.
        """
        if k is None:
            return NullOrder()

        return k

    @memoize
    def get_data_sorted(self):
        """
        Get the data contained in this column sorted.
        """
        return sorted(self.get_data(), key=self._null_handler)

    def aggregate(self, aggregation):
        """
        Apply a :class:`.Aggregation` to this column and return the result. If
        the aggregation defines a
        """
        cache_key = aggregation.get_cache_key()

        if cache_key is not None:
            if cache_key in self._aggregate_cache:
                return self._aggregate_cache[cache_key]

        result = aggregation.run(self)

        if cache_key is not None:
            self._aggregate_cache[cache_key] = result

        return result

class ColumnMapping(Mapping):
    """
    Proxy access to :class:`Column` instances for :class:`.Table`.

    :param table: :class:`.Table`.
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

    @memoize
    def __len__(self):
        return len(self._table._column_names)

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
