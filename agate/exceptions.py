#!/usr/bin/env python

"""
This module contains various exceptions raised by agate.
"""


class DataTypeError(TypeError):  # pragma: no cover
    """
    Exception raised if a process, such as an :class:`.Aggregation`, is
    attempted with an invalid data type.
    """
    pass


class UnsupportedAggregationError(TypeError):  # pragma: no cover
    """
    Exception raised if an aggregation is attempted which is not supported. For
    example if a :class:`.Percentiles` is used on a :class:`.TableSet`.
    """
    pass


class CastError(Exception):  # pragma: no cover
    """
    Exception raised when a column value can not be cast to the correct type.
    """
    pass


class FieldSizeLimitError(Exception):  # pragma: no cover
    """
    Exception raised when a field in the CSV file exceeds the default max
    or one provided by the user.
    """
    def __init__(self, limit):
        super(FieldSizeLimitError, self).__init__(
            'CSV contains fields longer than maximum length of %i characters. Try raising the maximum with the field_size_limit parameter, or try setting quoting=csv.QUOTE_NONE.' % limit
        )
