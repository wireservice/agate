#!/usr/bin/env python

from copy import copy

from agate.rows import Row


def compute(table, computations):
    """
    See :meth:`.Table.compute`.
    """
    column_names = list(copy(table.column_names))
    column_types = list(copy(table.column_types))

    for new_column_name, computation in computations:
        column_names.append(new_column_name)
        column_types.append(computation.get_computed_data_type(table))

        computation.validate(table)

    new_columns = tuple(c.run(table) for n, c in computations)
    new_rows = []

    for i, row in enumerate(table.rows):
        values = tuple(row) + tuple(c[i] for c in new_columns)
        new_rows.append(Row(values, column_names))

    return table._fork(new_rows, column_names, column_types)
