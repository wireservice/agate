#!/usr/bin/env python

"""
This module contains agate's :class:`Row` implementation. Rows are independent
of both the :class:`.Table` that contains them as well as the :class:`.Columns`
that access their data. This independence, combined with rows immutability
allows them to be safely shared between table instances.
"""

from agate.mapped_sequence import MappedSequence
from agate.utils import memoize


class Row(MappedSequence):
    """
    Proxy access to row data. Instances of :class:`Row` should
    not be constructed directly. They are created by :class:`.Table`
    instances and are unique to them.

    Rows are implemented as subclass of :class:`.MappedSequence`. They
    deviate from the underlying implementation in that loading of their data
    is deferred until it is needed.

    :param index:
        The numerical index of this row.
    :param columns:
        A :class:`.MappedSequence` that contains the :class:`.Column` instances
        containing the data for this row.
    :param column_names:
        An list of column names (keys) for this row.
    :param name:
        The name of this row (if any).
    """
    def __init__(self, index, columns, column_names, name=None):
        self._index = index
        self._columns = columns
        self._column_names = column_names
        self._name = name

    @property
    def index(self):
        """
        This row's index.
        """
        return self._index

    @property
    def name(self):
        """
        This row's name (if any).
        """
        return self._name

    def keys(self):
        """
        The column names for this column, if any.
        """
        return self._column_names

    @memoize
    def values(self):
        """
        Get the values in this column, as a tuple.
        """
        return tuple(column[self._index] for column in self._columns)
