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
    ), NullCalculationWarning, stacklevel=2)


class DuplicateColumnWarning(RuntimeWarning):  # pragma: no cover
    """
    Warning raised if multiple columns with the same name are added to a new
    :class:`.Table`.
    """
    pass


def warn_duplicate_column(column_name, column_rename):
    warnings.warn('Column name "%s" already exists in Table. Column will be renamed to "%s".' % (
        column_name,
        column_rename
    ), DuplicateColumnWarning, stacklevel=2)
