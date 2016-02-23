#!/usr/bin/env python

"""
This module contains the :class:`Column` class, which defines a "vertical"
array of tabular data. Whereas :class:`.Row` instances are independent of their
parent :class:`.Table`, columns depend on knowledge of both their position in
the parent (column name, data type) as well as the rows that contain their data.
"""
import six

from agate.mapped_sequence import MappedSequence
from agate.utils import NullOrder, memoize

if six.PY3:  # pragma: no cover
    # pylint: disable=W0622
    xrange = range


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
    instances and are unique to them.

    Columns are implemented as subclass of :class:`.MappedSequence`. They
    deviate from the underlying implementation in that loading of their data
    is deferred until it is needed.

    :param name:
        The name of this column.
    :param data_type:
        An instance of :class:`.DataType`.
    :param rows:
        A :class:`.MappedSequence` that contains the :class:`.Row` instances
        containing the data for this column.
    :param row_names:
        An optional list of row names (keys) for this column.
    """
    def __init__(self, index, name, data_type, rows, row_names=None):
        self._index = index
        self._name = name
        self._data_type = data_type
        self._rows = rows
        self._row_names = row_names

    @property
    def index(self):
        """
        This column's index.
        """
        return self._index

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

    def keys(self):
        """
        The row names for this column, if any.
        """
        return self._row_names

    @memoize
    def values(self):
        """
        Get the values in this column, as a tuple.
        """
        return tuple(row[self._index] for row in self._rows)

    @memoize
    def values_distinct(self):
        """
        Get the distinct values in this column, as a tuple.
        """
        return tuple(set(self.values()))

    @memoize
    def values_without_nulls(self):
        """
        Get the values in this column with any null values removed.
        """
        return tuple(d for d in self.values() if d is not None)

    @memoize
    def values_sorted(self):
        """
        Get the values in this column sorted.
        """
        return sorted(self.values(), key=null_handler)

    @memoize
    def values_without_nulls_sorted(self):
        """
        Get the values in this column with any null values removed and sorted.
        """
        return sorted(self.values_without_nulls(), key=null_handler)
