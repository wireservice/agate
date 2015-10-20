#!/usr/bin/env python

"""
This module contains the :class:`Column` class, which defines a "vertical"
array of tabular data. Whereas :class:`.Row` instances are independent of their
parent :class:`.Table`, columns depend on knowledge of both their position in
the parent (column name, data type) as well as the rows that contain their data.
"""

from collections import Sequence

import six

if six.PY3: #pragma: no cover
    #pylint: disable=W0622
    xrange = range

from agate.utils import MappedSequence, NullOrder, memoize

def null_handler(k):
    """
    Key method for sorting nulls correctly.
    """
    if k is None:
        return NullOrder()

    return k

class Column(MappedSequence):
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
    def __init__(self, name, data_type, rows, row_names=None):
        self._name = name
        self._data_type = data_type
        self._rows = rows
        self._row_names = row_names
        self._aggregate_cache = {}

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
    def keys(self):
        return self._row_names

    @memoize
    def values(self):
        return tuple(row[self._name] for row in self._rows)

    @memoize
    def dict(self):
        return dict(zip(self.keys(), self.values()))

    @memoize
    def values_without_nulls(self):
        """
        Get the data contained in this column with any null values removed.
        """
        return tuple(d for d in self.values() if d is not None)

    @memoize
    def values_sorted(self):
        """
        Get the data contained in this column sorted.
        """
        return sorted(self.values(), key=null_handler)

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
