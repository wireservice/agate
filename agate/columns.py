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
    A column of data. Values within a column can be accessed by row index or
    row name, if specified. Columns are immutable and may be shared between
    :class:`.Table` instances.
    """
    def __init__(self, values, data_type, row_names=None):
        self._data_type = data_type

        super(Column, self).__init__(values, row_names)

    @property
    def data_type(self):
        """
        This column's data type.
        """
        return self._data_type

    @memoize
    def values_distinct(self):
        """
        Get the distinct values in this column, as a tuple.
        """
        return tuple(set(self._values))

    @memoize
    def values_without_nulls(self):
        """
        Get the values in this column with any null values removed.
        """
        return tuple(d for d in self._values if d is not None)

    @memoize
    def values_sorted(self):
        """
        Get the values in this column sorted.
        """
        return sorted(self._values, key=null_handler)

    @memoize
    def values_without_nulls_sorted(self):
        """
        Get the values in this column with any null values removed and sorted.
        """
        return sorted(self.values_without_nulls(), key=null_handler)
