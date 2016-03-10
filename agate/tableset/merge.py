#!/usr/bin/env python

from agate.rows import Row
from agate.table import Table


def merge(table, groups, group_name, group_type):
    """
    See :meth:`.TableSet.merge`.
    """
    if type(groups) is not list and groups is not None:
        raise ValueError('Groups must be None or a list.')

    if type(groups) is list and len(groups) != len(table):
        raise ValueError('Groups length must be equal to TableSet length.')

    column_names = list(table.column_names)
    column_types = list(table.column_types)

    column_names.insert(0, group_name if group_name else table.key_name)
    column_types.insert(0, group_type if group_type else table.key_type)

    rows = []

    for index, (key, table) in enumerate(table.items()):
        for row in table.rows:
            if groups is None:
                rows.append(Row((key,) + tuple(row), column_names))
            else:
                rows.append(Row((groups[index],) + tuple(row), column_names))

    return Table(rows, column_names, column_types)
