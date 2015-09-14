#!/usr/bin/env python

"""
This module contains various exceptions raised by agate.
"""

class NullCalculationError(ValueError):  # pragma: no cover
    """
    Exception raised if a calculation which can not logically
    account for null values is attempted on a :class:`.Column` containing
    nulls.
    """
    pass

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

class CastError(Exception):   #pragma: no cover
    """
    Exception raised when a column value can not be cast to the correct type.
    """
    pass

class ColumnDoesNotExistError(Exception):  # pragma: no cover
    """
    Exception raised when trying to access a column that does
    not exist.

    :param k: The key used to access the non-existent :class:`.Column`.
    """
    def __init__(self, k):
        self._k = k

    def __unicode__(self):
        return 'Column `%s` does not exist.' % (self._k)

    def __str__(self):
        return str(self.__unicode__())

class RowDoesNotExistError(Exception):  # pragma: no cover
    """
    Exception raised when trying to access a row that does
    not exist.

    :param i: The index used to access the non-existent :class:`.Row`.
    """
    def __init__(self, i):
        self._i = i

    def __unicode__(self):
        return 'Row `%i` does not exist.' % (self._i)

    def __str__(self):
        return str(self.__unicode__())
