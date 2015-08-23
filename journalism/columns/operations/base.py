#!/usr/bin/env python

class ColumnOperation(object):
    """
    Base class defining an operation that can be performed on a column either
    to yield an individual value or as part of a :class:`.TableSet` aggregate.
    """
    def __init__(self, column):
        self._column = column

    def get_aggregate_column_type(self):
        raise NotImplementedError()

    def __call__(self):
        raise NotImplementedError()

class HasNulls(ColumnOperation):
    """
    Returns :code:`True` if this column contains null values.
    """
    def get_aggregate_column_type(self):
        return BooleanType()

    def __call__(self):
        return None in self._column._data()

class Any(ColumnOperation):
    """
    Returns :code:`True` if any value passes a truth test.

    :param test: A function that takes a value and returns :code:`True`
        or :code:`False`.
    """
    def get_aggregate_column_type(self):
        return BooleanType()

    def __call__(self, test):
        return any(test(d) for d in self._column._data())

class All(ColumnOperation):
    """
    Returns :code:`True` if all values pass a truth test.

    :param test: A function that takes a value and returns :code:`True`
        or :code:`False`.
    """
    def get_aggregate_column_type(self):
        return BooleanType()

    def __call__(self, test):
        return all(test(d) for d in self._column._data())

class Count(ColumnOperation):
    """
    Count the number of times a specific value occurs in this column.

    :param value: The value to be counted.
    """
    def get_aggregate_column_type(self):
        return NumberType()

    def __call__(self, value):
        count = 0

        for d in self._column._data():
            if d == value:
                count += 1

        return count
