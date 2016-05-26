#!/usr/bin/env python
# pylint: disable=W0212

from agate.utils import slugify


def rename(self, column_names=None, row_names=None, slugify_names=False, **kwargs):
    """
    Create a copy of this table with different column names or row names.

    :code:`kwargs` will be passed through to the Slugify class.
    (https://github.com/dimka665/awesome-slugify)

    :param column_names:
        New column names for the renamed table. May be either an array or
        a dictionary mapping existing column names to new names. If not
        specified, will use this table's existing column names.
    :param row_names:
        New row names for the renamed table. May be either an array or
        a dictionary mapping existing row names to new names. If not
        specified, will use this table's existing row names.
    :param slugify_names:
        If True, given column and row names will be standardized and duplicate
        names will be given unique identifiers.
    """
    from agate.table import Table

    if isinstance(column_names, dict):
        column_names = [column_names[name] if name in column_names else name for name in self._column_names]

    if isinstance(row_names, dict):
        row_names = [row_names[name] if name in row_names else name for name in self._row_names]

    if slugify_names:
        if column_names is not None:
            column_names = slugify(column_names, ensure_unique=True, **kwargs)

        if row_names is not None:
            row_names = slugify(row_names, ensure_unique=True, **kwargs)

    if column_names is not None and column_names != self._column_names:
        if row_names is None:
            row_names = self._row_names

        return Table(self._rows, column_names, self._column_types, row_names=row_names, _is_fork=False)
    else:
        return self._fork(self._rows, column_names, self._column_types, row_names=row_names)
