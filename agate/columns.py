#!/usr/bin/env python

from collections import Sequence

import six

if six.PY3: #pragma: no cover
    #pylint: disable=W0622
    xrange = range

from agate.utils import MappedSequence, NullOrder, memoize

class Column(Sequence):
    """
    Proxy access to column data. Instances of :class:`Column` should
    not be constructed directly. They are created by :class:`.Table`
    instances.

    Column instances are unique to the :class:`.Table` with which they are
    associated.

    :param name: The name of this column.
    :param data_type: An instance of :class:`.DataType`.
    :param rows: The :class:`.RowSequence` that contains data for this column.
    """
    def __init__(self, name, data_type, rows):
        self._name = name
        self._data_type = data_type
        self._rows = rows
        self._aggregate_cache = {}

    def __unicode__(self):
        data = self.get_data()

        sample = u', '.join(repr(d) for d in data[:5])

        if len(data) > 5:
            sample = u'%s, ...' % sample

        return u'<agate.Column: (%s)>' % (sample)

    def __str__(self):
        if six.PY2:
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())  #pragma: no cover

    def __getitem__(self, k):
        return self.get_data()[k]

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
    def name(self):
        """
        This column's name.
        """
        return self._name

    @property
    def data_type(self):
        """
        This column's data type.
        """
        return self._data_type

    @memoize
    def get_data(self):
        """
        Get the data contained in this column as a :class:`tuple`.
        """
        return tuple(row[self._name] for row in self._rows)

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
        the aggregation defines a `cache_key` the result will be cached for
        future requests.
        """
        cache_key = aggregation.get_cache_key()

        if cache_key is not None:
            if cache_key in self._aggregate_cache:
                return self._aggregate_cache[cache_key]

        result = aggregation.run(self)

        if cache_key is not None:
            self._aggregate_cache[cache_key] = result

        return result

class ColumnSequence(MappedSequence):
    """
    A sequence of :class:`Column` instances. Instances can be accessed either by
    numeric index or by column name.

    :param column_names: The names of the columns.
    :param columns: The :class:`.Column` instances.
    """
    def __init__(self, column_names, columns):
        super(ColumnSequence, self).__init__(columns, column_names)
