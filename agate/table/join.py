#!/usr/bin/env python

from agate.rows import Row
from agate import utils

def join(table, right_table, left_key, right_key=None, inner=False, require_match=False, columns=None):
    """
    See :meth:`.Table.join`.
    """
    if right_key is None:
        right_key = left_key

    # Get join columns
    right_key_indices = []

    left_key_is_func = hasattr(left_key, '__call__')
    left_key_is_sequence = utils.issequence(left_key)

    # Left key is a function
    if left_key_is_func:
        left_data = [left_key(row) for row in table.rows]
    # Left key is a sequence
    elif left_key_is_sequence:
        left_columns = [table.columns[key] for key in left_key]
        left_data = zip(*[column.values() for column in left_columns])
    # Left key is a column name/index
    else:
        left_data = table.columns[left_key].values()

    right_key_is_func = hasattr(right_key, '__call__')
    right_key_is_sequence = utils.issequence(right_key)

    # Right key is a function
    if right_key_is_func:
        right_data = [right_key(row) for row in right_table.rows]
    # Right key is a sequence
    elif right_key_is_sequence:
        right_columns = [right_table.columns[key] for key in right_key]
        right_data = zip(*[column.values() for column in right_columns])
        right_key_indices = [right_table.columns._keys.index(key) for key in right_key]
    # Right key is a column name/index
    else:
        right_column = right_table.columns[right_key]
        right_data = right_column.values()
        right_key_indices = [right_table.columns._keys.index(right_key)]

    # Build names and type lists
    column_names = list(table.column_names)
    column_types = list(table.column_types)

    for i, column in enumerate(right_table.columns):
        name = column.name

        if columns is None and i in right_key_indices:
            continue

        if columns is not None and name not in columns:
            continue

        if name in table.column_names:
            column_names.append('%s2' % name)
        else:
            column_names.append(name)

        column_types.append(column.data_type)

    if columns is not None:
        right_table = right_table.select([n for n in right_table.column_names if n in columns])

    right_hash = {}

    for i, value in enumerate(right_data):
        if value not in right_hash:
            right_hash[value] = []

        right_hash[value].append(right_table.rows[i])

    # Collect new rows
    rows = []

    if table.row_names is not None:
        row_names = []
    else:
        row_names = None

    # Iterate over left column
    for left_index, left_value in enumerate(left_data):
        matching_rows = right_hash.get(left_value, None)

        if require_match and matching_rows is None:
            raise ValueError('Left key "%s" does not have a matching right key.' % left_value)

        # Rows with matches
        if matching_rows:
            for right_row in matching_rows:
                new_row = list(table.rows[left_index])

                for k, v in enumerate(right_row):
                    if columns is None and k in right_key_indices:
                        continue

                    new_row.append(v)

                rows.append(Row(new_row, column_names))

                if table.row_names is not None:
                    row_names.append(table.row_names[left_index])
        # Rows without matches
        elif not inner:
            new_row = list(table.rows[left_index])

            for k, v in enumerate(right_table.column_names):
                if columns is None and k in right_key_indices:
                    continue

                new_row.append(None)

            rows.append(Row(new_row, column_names))

            if table.row_names is not None:
                row_names.append(table.row_names[left_index])

    return table._fork(rows, column_names, column_types, row_names=row_names)
