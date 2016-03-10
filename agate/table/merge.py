#!/usr/bin/env python

from collections import OrderedDict

from agate.exceptions import DataTypeError
from agate.rows import Row
from agate.table import Table

def merge(tables, row_names, column_names):
    """
    See :meth:`.Table.merge`.
    """
    new_columns = OrderedDict()

    for table in tables:
        for i in range(0, len(table.columns)):
            if column_names is None or table.column_names[i] in column_names:
                column_name = table.column_names[i]
                column_type = table.column_types[i]

                if column_name in new_columns:
                    if not isinstance(column_type, type(new_columns[column_name])):
                        raise DataTypeError('Tables contain columns with the same names, but different types.')
                else:
                    new_columns[column_name] = column_type

    column_keys = new_columns.keys()
    column_types = new_columns.values()

    rows = []

    for table in tables:
        # Performance optimization for identical table structures
        if table.column_names == column_keys and table.column_types == column_types:
            rows.extend(table.rows)
        else:
            for row in table.rows:
                data = []

                for column_key in column_keys:
                    data.append(row.get(column_key, None))

                rows.append(Row(data, column_keys))

    return Table(rows, column_keys, column_types, row_names=row_names, _is_fork=True)
