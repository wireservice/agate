#!/usr/bin/env python

import datetime

import pytimeparse
import six

from agate.data_types.base import DataType
from agate.exceptions import CastError

class TimeDelta(DataType):
    """
    Data type representing the interval between two times.
    """
    def test(self, d):
        """
        Test, for purposes of type inference, if a string value could possibly
        be valid for this column type.
        """
        d = d.strip()

        if d.lower() in self.null_values:
            return True

        seconds = pytimeparse.parse(d)

        if seconds is None:
            return False

        return True

    def cast(self, d):
        """
        Cast a single value to :class:`datetime.timedelta`.

        :param d: A value to cast.
        :returns: :class:`datetime.timedelta` or :code:`None`
        """
        if isinstance(d, datetime.timedelta) or d is None:
            return d
        elif isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        seconds = pytimeparse.parse(d)

        if seconds is None:
            raise CastError('Can not parse value "%s" to as timedelta.' % d)

        return datetime.timedelta(seconds=seconds)
