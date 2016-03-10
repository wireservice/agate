#!/usr/bin/env python

from agate.table import Table
from agate.data_types import TypeTester
from agate.rows import Row
from agate import utils

def normalize(table, key, properties, property_column='property', value_column='value', column_types=None):
    """
    See :meth:`.Table.normalize`.
    """
    new_rows = []

    if not utils.issequence(key):
        key = [key]

    if not utils.issequence(properties):
        properties = [properties]

    new_column_names = key + [property_column, value_column]

    row_names = []

    for row in table.rows:
        k = tuple(row[n] for n in key)
        left_row = list(k)

        if len(k) == 1:
            row_names.append(k[0])
        else:
            row_names.append(k)

        for f in properties:
            new_rows.append(Row(tuple(left_row + [f, row[f]]), new_column_names))

    key_column_types = [table.column_types[table.column_names.index(name)] for name in key]

    if column_types is None or isinstance(column_types, TypeTester):
        tester = TypeTester() if column_types is None else column_types
        force_update = dict(zip(key, key_column_types))
        force_update.update(tester._force)
        tester._force = force_update

        new_column_types = tester.run(new_rows, new_column_names)
    else:
        new_column_types = key_column_types + list(column_types)

    return Table(new_rows, new_column_names, new_column_types, row_names=row_names)
