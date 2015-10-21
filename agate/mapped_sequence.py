#!/usr/bin/env python

"""
This module contains the :class:`MappedSequence` class that forms the foundation
for agate's :class:`.Row` and :class:`.Column` as well as for named sequences of
rows and columns.
"""

from collections import Sequence

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

import six
from six.moves import range #pylint: disable=W0622

from agate.utils import memoize

class MappedSequence(Sequence):
    """
    A generic container for data that can be accessed either by numeric index
    or by key. This is similar to an :class:`collections.OrderedDict` except
    that the keys are optional and iteration over it returns the values.

    :param rows: A sequence of :class:`Row` instances.
    :param row_alias: See :meth:`.Table.__init__`.
    """
    def __init__(self, values, keys=None):
        self._values = tuple(values)

        if keys is not None:
            self._keys = tuple(keys)
        else:
            self._keys = None

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
        if six.PY2: #pragma: no cover
            return str(self.__unicode__().encode('utf8'))

        return str(self.__unicode__())

    def __getitem__(self, key):
        """
        Retrieve values from this array by index, by slice or by key.
        """
        if isinstance(key, slice):
            indices = range(*key.indices(len(self)))
            values = self.values()

            return tuple(values[i] for i in indices)
        # Note: can't use isinstance because bool is a subclass of int
        elif type(key) is int:
            return self.values()[key]
        else:
            return self.dict()[key]

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
        if not isinstance(other, Sequence):
            return False

        return self.values() == tuple(other)

    def __ne__(self, other):
        """
        Inequality test with other sequences.
        """
        return not self.__eq__(other)

    def __contains__(self, value):
        return self.values().__contains__(value)

    def keys(self):
        """
        Equivalent to :meth:`collections.OrderedDict.keys`.
        """
        return self._keys

    def values(self):
        """
        Equivalent to :meth:`collections.OrderedDict.values`.
        """
        return self._values

    @memoize
    def items(self):
        """
        Equivalent to :meth:`collections.OrderedDict.items`.
        """
        return tuple(zip(self.keys(), self.values()))

    def get(self, key, default=None):
        """
        Equivalent to :meth:`collections.OrderedDict.get`.
        """
        try:
            return self.dict()[key]
        except KeyError:
            if default:
                return default

            raise

    @memoize
    def dict(self):
        """
        Retrieve the contents of this column as an :class:`collections.OrderedDict`.
        """
        if self.keys() is None:
            raise KeyError

        return OrderedDict(self.items())
