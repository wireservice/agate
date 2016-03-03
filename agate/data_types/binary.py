#!/usr/bin/env python

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

import six

from agate.data_types.base import DataType, DEFAULT_NULL_VALUES
from agate.exceptions import CastError

class Binary(DataType):
    """
    Data type representing Binary values.

    Note: numerical `1` and `0` are considered valid binary values, but no
    other numbers are.

    """
    def __init__(self, null_values=DEFAULT_NULL_VALUES):
        super(Binary, self).__init__(null_values=null_values)

    def cast(self, d):
        """
        Cast a single value to :class:`bool`.

        :param d: A value to cast.
        :returns: :class:`bool` or :code:`None`.
        """

        if d is None:
            return d
        elif type(d) is int or isinstance(d, Decimal):
            if d == 0 or d == 1:
                return d
        elif isinstance(d, six.string_types):
            d = d.replace(',', '').strip()
            
            if d in self.null_values:
                return None
            elif d == '0' or d == '1':
                return int(d)

        raise CastError('Can not convert value %s to binary.' % d)

    def jsonify(self, d):
        return d
