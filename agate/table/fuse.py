#!/usr/bin/env python
# pylint: disable=W0212

from agate.rows import Row
from agate import utils


def fuse(self, right_table):
    """
    Join two tables by aligning them horizontally without performing any
    filtering. This is effectively a "join by row number".

    :param right_table:
        The "right" table to join to.
    :returns:
        A new :class:`.Table`.
    """
    len_left = len(self._columns)
    len_right = len(right_table._columns)

    left_rows = (list(r) for r in self._rows)
    right_rows = (list(r) for r in right_table._rows)

    column_names = self._column_names + right_table._column_names
    column_types = self._column_types + right_table._column_types

    new_rows = []

    for left_row in left_rows:
        try:
            right_row = next(right_rows)
            new_rows.append(Row(left_row + right_row, column_names))
        except StopIteration:
            new_rows.append(Row(left_row + ([None] * len_right), column_names))

    for right_row in right_rows:
        new_rows.append(Row(([None] * len_left) + right_row, column_names))

    return self._fork(new_rows, column_names, column_types)
