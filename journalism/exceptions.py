#!/usr/bin/env python

class NullComputationError(Exception):  # pragma: no cover
    """
    Exception raised if an computation which can not logically
    account for null values is attempted on a Column containing
    nulls.
    """
    pass

class UnsupportedOperationError(Exception):  # pragma: no cover
    """
    Exception raised when an operation is applied
    to a column type that does not support it.

    :param operation: The name of the operation.
    :param column: The :class:`.Column` it was applied to.
    """
    def __init__(self, operation, column):
        self.operation = operation
        self.column = column

    def __unicode__(self):
        return '`%s` is not a supported operation for %s' % (self.operation, type(self.column))

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

    :param k: The key used to access the non-existaent :class:`.Column`.
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
