#!/usr/bin/env python

import warnings

class NullCalculationWarning(RuntimeWarning):  # pragma: no cover
    """
    Warning raised if a calculation which can not logically
    account for null values is performed on a :class:`.Column` containing
    nulls.
    """
    pass

def warn_null_calculation(operation, column):
    warnings.warn('Column "%s" contains nulls. These will be excluded from %s calculation.' % (
        column.name,
        operation.__class__.__name__
    ), NullCalculationWarning)
