#!/usr/bin/env python

import six

from agate.data_types.base import DataType

class Text(DataType):
    """
    Data type representing text.
    """
    def test(self, d):
        """
        Test, for purposes of type inference, if a value could possibly be valid
        for this column type. This will work with values that are native types
        and values that have been stringified.
        """
        return True

    def cast(self, d):
        """
        Cast a single value to :func:`unicode` (:func:`str` in Python 3).

        :param d:
            A value to cast.
        :returns:
            :func:`unicode` (:func:`str` in Python 3) or :code:`None`
        """
        if d is None:
            return d
        elif isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        return six.text_type(d)
