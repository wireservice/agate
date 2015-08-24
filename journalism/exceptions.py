#!/usr/bin/env python

class NullComputationError(Exception):  # pragma: no cover
    """
    Exception raised if an computation which can not logically
    account for null values is attempted on a Column containing
    nulls.
    """
    pass

class UnsupportedAggregationError(Exception):  # pragma: no cover
    """
    Exception raised if an computation is applied to a column where it is not
    supported or it is not logically possible to complete it.
    """
    def __init__(self, aggregation, column):
        self.aggregation = aggregation
        self.column = column

    def __unicode__(self):
        return '`%s` is not a supported operation for %s' % (type(self.aggregation), type(self.column))

    def __str__(self):
        return str(self.__unicode__())

class UnsupportedComputationError(Exception):  # pragma: no cover
    """
    Exception raised when a :class:`.Computation` is applied to a column type
    that does not support it.

    :param computation: The :class:`.Computation` being applied.
    :param column: The :class:`.Column` it was applied to.
    """
    def __init__(self, computation, column):
        self.computation = computation
        self.column = column

    def __unicode__(self):
        return '`%s` is not a supported computation for %s' % (type(self.computation), type(self.column))

    def __str__(self):
        return str(self.__unicode__())

class CastError(Exception):   #pragma: no cover
    """
    Exception raised when a column value can not be cast to
    the correct type.
    """
    pass

class ColumnDoesNotExistError(Exception):  # pragma: no cover
    """
    Exception raised when trying to access a column that does
    not exist.

    :param k: The key used to access the non-existent :class:`.Column`.
    """
    def __init__(self, k):
        self.k = k

    def __unicode__(self):
        return 'Column `%s` does not exist.' % (self.k)

    def __str__(self):
        return str(self.__unicode())

class RowDoesNotExistError(Exception):  # pragma: no cover
    """
    Exception raised when trying to access a row that does
    not exist.

    :param i: The index used to access the non-existent :class:`.Row`.
    """
    def __init__(self, i):
        self.i = i

    def __unicode__(self):
        return 'Row `%i` does not exist.' % (self.i)

    def __str__(self):
        return str(self.__unicode())
