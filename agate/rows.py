#!/usr/bin/env python

"""
This module contains agate's :class:`Row` implementation. Rows are independent
of both the :class:`.Table` that contains them as well as the :class:`.Columns`
that access their data. This independence, combined with rows immutability
allows them to be shared between table instances.
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
    #pylint: disable=E1101

    def __init__(self, column_names, data):
        MappedSequence.__init__(self, data, column_names)

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
