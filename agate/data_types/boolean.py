#!/usr/bin/env python

import six

from agate.data_types.base import DataType, DEFAULT_NULL_VALUES
from agate.exceptions import CastError

#: Default values which will be automatically cast to :code:`True`.
DEFAULT_TRUE_VALUES = ('yes', 'y', 'true', 't')

#: Default values which will be automatically cast to :code:`False`.
DEFAULT_FALSE_VALUES = ('no', 'n', 'false', 'f')

class Boolean(DataType):
    """
    Data type representing boolean values.

    :param true_values: A sequence of values which should be cast to
        :code:`True` when encountered with this type.
    :param false_values: A sequence of values which should be cast to
        :code:`False` when encountered with this type.
    """
    def __init__(self, true_values=DEFAULT_TRUE_VALUES, false_values=DEFAULT_FALSE_VALUES, null_values=DEFAULT_NULL_VALUES):
        super(Boolean, self).__init__(null_values=null_values)

        self.true_values = true_values
        self.false_values = false_values

    def test(self, d):
        """
        Test, for purposes of type inference, if a string value could possibly
        be valid for this column type.
        """
        d = d.replace(',' ,'').strip()

        d_lower = d.lower()

        if d_lower in self.null_values:
            return True
        elif d_lower in self.true_values:
            return True
        elif d_lower in self.false_values:
            return True

        return False

    def cast(self, d):
        """
        Cast a single value to :class:`bool`.

        :param d: A value to cast.
        :returns: :class:`bool` or :code:`None`.
        """
        if isinstance(d, bool) or d is None:
            return d
        elif isinstance(d, six.string_types):
            d = d.replace(',' ,'').strip()

            d_lower = d.lower()

            if d_lower in self.null_values:
                return None
            elif d_lower in self.true_values:
                return True
            elif d_lower in self.false_values:
                return False

        raise CastError('Can not convert value %s to bool.' % d)
