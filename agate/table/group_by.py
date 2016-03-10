#!/usr/bin/env python

from collections import OrderedDict

from agate.data_types import Text
from agate.tableset import TableSet


def group_by(table, key, key_name, key_type):
    """
    See :meth:`.Table.group_by`.
    """


    key_is_row_function = hasattr(key, '__call__')

    if key_is_row_function:
        key_name = key_name or 'group'
        key_type = key_type or Text()
    else:
        column = table.columns[key]

        key_name = key_name or column.name
        key_type = key_type or column.data_type

    groups = OrderedDict()

    for row in table.rows:
        if key_is_row_function:
            group_name = key(row)
        else:
            group_name = row[column.name]

        group_name = key_type.cast(group_name)

        if group_name not in groups:
            groups[group_name] = []

        groups[group_name].append(row)

    output = OrderedDict()

    for group, rows in groups.items():
        output[group] = table._fork(rows)

    return TableSet(output.values(), output.keys(), key_name=key_name, key_type=key_type)
