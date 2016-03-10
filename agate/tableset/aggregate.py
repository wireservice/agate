#!/usr/bin/env python

from agate.table import Table
from agate.tableset import TableSet


def _aggregate(tableset, aggregations):
    """
    Recursive aggregation allowing for TableSet's to be nested inside
    one another.
    """
    output = []

    # Process nested TableSet's
    if isinstance(tableset._values[0], TableSet):
        for key, nested_tableset in tableset.items():
            column_names, column_types, nested_output, row_name_columns = _aggregate(nested_tableset, aggregations)

            for row in nested_output:
                row.insert(0, key)

                output.append(row)

        column_names.insert(0, tableset.key_name)
        column_types.insert(0, tableset.key_type)
        row_name_columns.insert(0, tableset.key_name)
    # Regular Tables
    else:
        column_names = [tableset.key_name]
        column_types = [tableset.key_type]
        row_name_columns = [tableset.key_name]

        for new_column_name, aggregation in aggregations:
            column_names.append(new_column_name)
            column_types.append(aggregation.get_aggregate_data_type(tableset._sample_table))

        for name, table in tableset.items():
            for new_column_name, aggregation in aggregations:
                aggregation.validate(table)

        for name, table in tableset.items():
            new_row = [name]

            for new_column_name, aggregation in aggregations:
                new_row.append(aggregation.run(table))

            output.append(new_row)

    return column_names, column_types, output, row_name_columns

def aggregate(tableset, aggregations):
    """
    See :meth:`.TableSet.aggregate`.
    """
    column_names, column_types, output, row_name_columns = _aggregate(tableset, aggregations)

    if len(row_name_columns) == 1:
        row_names = row_name_columns[0]
    else:
        def row_names(r):
            return tuple(r[n] for n in row_name_columns)

    return Table(output, column_names, column_types, row_names=row_names)
