#!/usr/bin/env python
# pylint: disable=W0212

from agate import utils


def rename(self, column_names=None, row_names=None, slug_columns=False, slug_rows=False, **kwargs):
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
        If True, given column and row names will be converted to slugs and
        duplicate names will be given unique identifiers.
    """
    from agate.table import Table

    if isinstance(column_names, dict):
        column_names = [column_names[name] if name in column_names else name for name in self._column_names]

    if isinstance(row_names, dict):
        row_names = [row_names[name] if name in row_names else name for name in self._row_names]

    if slug_columns:
        column_names = column_names or self._column_names

        if column_names is not None:
            column_names = utils.slugify(column_names, ensure_unique=True, **kwargs)

    if slug_rows:
        row_names = row_names or self.row_names

        if row_names is not None:
            row_names = utils.slugify(row_names, ensure_unique=True, **kwargs)

    if column_names is not None and column_names != self._column_names:
        if row_names is None:
            row_names = self._row_names

        print (column_names)

        return Table(self._rows, column_names, self._column_types, row_names=row_names, _is_fork=False)
    else:
        return self._fork(self._rows, column_names, self._column_types, row_names=row_names)
