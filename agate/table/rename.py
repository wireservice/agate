#!/usr/bin/env python


def rename(self, column_names=None, row_names=None):
    """
    Create a copy of this table with different column names or row names.

    :param column_names:
        New column names for the renamed table. May be either an array or
        a dictionary mapping existing column names to new names. If not
        specified, will use this table's existing column names.
    :param row_names:
        New row names for the renamed table. May be either an array or
        a dictionary mapping existing row names to new names. If not
        specified, will use this table's existing row names.
    """
    from agate.table import Table

    if isinstance(column_names, dict):
        column_names = [column_names[name] if name in column_names else name for name in self.column_names]

    if isinstance(row_names, dict):
        row_names = [row_names[name] if name in row_names else name for name in self.row_names]

    if column_names is not None and column_names != self.column_names:
        if row_names is None:
            row_names = self._row_names

        return Table(self.rows, column_names, self.column_types, row_names=row_names, _is_fork=False)
    else:
        return self._fork(self.rows, column_names, self._column_types, row_names=row_names)
