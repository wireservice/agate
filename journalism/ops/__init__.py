#!/usr/bin/env python

import math

from journalism.columns import TextColumn, IntColumn, FloatColumn
from journalism.exceptions import NullComputationError, UnsupportedOperationError

def supported_columns(column_types):
    def wrapper(func):
        def check(column_type, data):
            if column_type not in column_types:
                raise UnsupportedOperationError

            return func(column_type, data)

        return check

    return wrapper

def no_null_computations(func):
    """
    Function decorator that prevents illogical computations
    on columns containing nulls.
    """
    def check(l, *args, **kwargs):
        if l.has_nulls():
            raise NullComputationError()

        return func(l)

    return check

def _without_nulls(data):
    return [d for d in data if d is not None]

@supported_columns([TextColumn, IntColumn, FloatColumn])
def validate(column_type, data):
    if column_type is TextColumn:
        test = lambda d: not isinstance(d, basestring) and d is not None
    elif column_type is IntColumn:
        test = lambda d: not isinstance(d, int) and d is not None
    elif column_type is FloatColumn:
        test = lambda d: not isinstance(d, float) and d is not None

    return any(data, test)

@supported_columns([IntColumn, FloatColumn])
def sum(column_type, data):
    return __builtins__['sum'](_without_nulls(data))

@supported_columns([IntColumn, FloatColumn])
def min(data):
    return min(_without_nulls(data))

@supported_columns([IntColumn, FloatColumn])
def max(data):
    return max(_without_nulls(data))

@no_null_computations
@supported_columns([IntColumn, FloatColumn])
def mean(data):
    return float(sum(data) / len(data))

@no_null_computations
@supported_columns([IntColumn, FloatColumn])
def median(data):
    length = len(data) 

    if length % 2 == 1:
        return data[((length + 1) / 2) - 1]
    else:
        a = data[(length / 2) - 1]
        b = data[length / 2]
    return (float(a + b)) / 2  

@no_null_computations
@supported_columns([IntColumn, FloatColumn])
def mode(data):
    # TODO
    pass

@no_null_computations
@supported_columns([IntColumn, FloatColumn])
def stdev(data):
    return math.sqrt(sum(math.pow(v - mean(data), 2) for v in data) / len(data))

