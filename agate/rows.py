#!/usr/bin/env python

"""
This module contains agate's :class:`Row` implementation and various related
classes. In common usage nothing in this module should need to be instantiated
directly.
"""

from collections import Mapping, Sequence

import six

if six.PY3: #pragma: no cover
    #pylint: disable=W0622
    xrange = range

from agate.exceptions import ColumnDoesNotExistError, RowDoesNotExistError
from agate.utils import memoize

class Row(Mapping):
    """
    A row of data. Values within a row can be accessed by column name or column
    index.

    Row instances are immutable and may be shared between :class:`.Table`
    instances.

    :param column_names: The "keys" for this row.
    :param data: The "values" for this row.
    """
    #pylint: disable=W0212

    def __init__(self, column_names, data):
        self._column_names = column_names
        self._data = data

    def __unicode__(self):
        sample = u', '.join(repr(d) for d in self._data[:5])

        if len(self._data) > 5:
            sample = u'%s, ...' % sample

        return u'<agate.Row: (%s)>' % sample

    def __str__(self):
        if six.PY2:
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())

    def __getitem__(self, k):
        if isinstance(k, int):
            try:
                return self._data[k]
            except IndexError:
                raise ColumnDoesNotExistError(k)

        try:
            j = self._column_names.index(k)
        except ValueError:
            raise ColumnDoesNotExistError(k)

        return self._data[j]

    @memoize
    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __eq__(self, other):
        return self._data == other

class RowSequence(Sequence):
    """
    A sequence of :class:`Row` instances. Instances can be accessed by numeric
    index or row alias (if specified).

    :param rows: A sequence of :class:`Row` instances.
    :param row_alias: See :meth:`.Table.__init__`.
    """
    def __init__(self, rows, row_alias=None):
        self._rows = rows
        self._row_alias = row_alias
        self._row_map = {}

        if self._row_alias:
            for i, row in enumerate(self._rows):
                if isinstance(row_alias, six.string_types):
                    alias = row[row_alias]
                else:
                    alias = tuple([row[k] for k in row_alias])

                if alias in self._row_map:
                    raise ValueError(u'Row alias was not unique: %s' % alias)

                self._row_map[alias] = i

    def __getitem__(self, k):
        if isinstance(k, slice):
            indices = xrange(*k.indices(len(self)))

            return tuple(self._rows[row] for row in indices)
        elif isinstance(k, int):
            try:
                return self._rows[k]
            except IndexError:
                raise RowDoesNotExistError(k)
        else:
            try:
                return self._rows[self._row_map[k]]
            except KeyError:
                raise RowDoesNotExistError(k)

    def __iter__(self):
        return iter(self._rows)

    @memoize
    def __len__(self):
        return len(self._rows)

    @property
    def row_alias(self):
        return self._row_alias

    def get_column_data(self, i):
        """
        Iterates over the rows and returns the data for a given column index.
        """
        return tuple(row[i] for row in self._rows)
