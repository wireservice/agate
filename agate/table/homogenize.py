#!/usr/bin/env python

from agate.rows import Row
from agate import utils

def homogenize(table, key, compare_values, default_row):
    """
    See :meth:`.Table.homogenize`.
    """
    rows = list(table.rows)

    if not utils.issequence(key):
        key = [key]

    if len(key) == 1:
        if any(not utils.issequence(compare_value) for compare_value in compare_values):
            compare_values = [[compare_value] for compare_value in compare_values]

    column_values = [table.columns.get(name) for name in key]
    column_indexes = [table.column_names.index(name) for name in key]

    column_values = zip(*column_values)
    differences = list(set(map(tuple, compare_values)) - set(column_values))

    for difference in differences:
        if callable(default_row):
            rows.append(Row(default_row(difference), table.column_names))
        else:
            if default_row is not None:
                new_row = default_row
            else:
                new_row = [None] * (len(table.column_names) - len(key))

            for i, d in zip(column_indexes, difference):
                new_row.insert(i, d)

            rows.append(Row(new_row, table.column_names))

    return table._fork(rows, table.column_names, table.column_types)
