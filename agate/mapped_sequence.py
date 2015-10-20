#!/usr/bin/env python

"""
This module contains the :class:`MappedSequence` class that forms the foundation
for agate's :class:`.Row` and :class:`.Column` as well as for named sequences of
rows and columns.
"""

from collections import OrderedDict, Sequence

import six
from six.moves import range #pylint: disable=W0622

from agate.utils import memoize

class MappedSequence(Sequence):
    """
    A generic container for data that can be accessed either by numeric index
    or by name. This is similar to an :class:`collections.OrderedDict` except
    that iteration over it returns values rather than keys.

    :param rows: A sequence of :class:`Row` instances.
    :param row_alias: See :meth:`.Table.__init__`.
    """
    def __init__(self, values, keys=None):
        self._values = values
        self._keys = keys

    def __unicode__(self):
        """
        Print a unicode sample of the contents of this sequence.
        """
        sample = u', '.join(repr(d) for d in self.values()[:5])

        if len(self) > 5:
            sample = u'%s, ...' % sample

        return u'<agate.%s: (%s)>' % (type(self).__name__, sample)

    def __str__(self):
        """
        Print a non-unicode sample of the contents of this sequence.
        """
        if six.PY2:
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())  #pragma: no cover

    def __getitem__(self, k):
        """
        Retrieve values from this array by index, by slice or by key.
        """
        if isinstance(k, slice):
            indices = range(*k.indices(len(self)))
            values = self.values()

            return tuple(values[i] for i in indices)
        elif isinstance(k, int):
            return self.values()[k]
        else:
            return self.dict()[k]

    def __iter__(self):
        """
        Iterate over values.
        """
        return iter(self.values())

    @memoize
    def __len__(self):
        return len(self.values())

    def __eq__(self, other):
        """
        Equality test with other sequences.
        """
        return self.values() == other

    def __ne__(self, other):
        """
        Inequality test with other sequences.
        """
        return not self.__eq__(other)

    def keys(self):
        return self._keys

    def values(self):
        return self._values

    @memoize
    def dict(self):
        """
        Get the contents of this column as an :class:`collections.OrderedDict`.
        """
        if not self._keys:
            raise KeyError

        return OrderedDict(zip(self._keys, self._values))
