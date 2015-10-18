#!/usr/bin/env python

"""
This module contains agate's :class:`Row` implementation and various related
classes. In common usage nothing in this module should need to be instantiated
directly.
"""

import six

if six.PY3: #pragma: no cover
    #pylint: disable=W0622
    xrange = range

from agate.utils import MappedSequence

class Row(MappedSequence):
    """
    A row of data. Values within a row can be accessed by column name or column
    index.

    Row instances are immutable and may be shared between :class:`.Table`
    instances.

    :param column_names: The "keys" for this row.
    :param data: The "values" for this row.
    """
    def __init__(self, column_names, data):
        super(Row, self).__init__(data, column_names)

    def __unicode__(self):
        sample = u', '.join(repr(d) for d in self._values[:5])

        if len(self._values) > 5:
            sample = u'%s, ...' % sample

        return u'<agate.Row: (%s)>' % sample

    def __str__(self):
        if six.PY2:
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())

    def __eq__(self, other):
        return self._values == other

class RowSequence(MappedSequence):
    """
    A sequence of :class:`Row` instances. Instances can be accessed by numeric
    index or row alias (if specified).

    :param rows: A sequence of :class:`Row` instances.
    :param row_alias: See :meth:`.Table.__init__`.
    """
    def __init__(self, rows, row_alias=None):
        aliases = []

        if row_alias:
            for i, row in enumerate(rows):
                if isinstance(row_alias, six.string_types):
                    alias = row[row_alias]
                else:
                    alias = tuple([row[k] for k in row_alias])

                if alias in aliases:
                    raise ValueError(u'Row alias was not unique: %s' % alias)

                aliases.append(alias)

        super(RowSequence, self).__init__(rows, aliases)
