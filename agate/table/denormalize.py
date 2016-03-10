#!/usr/bin/env python

from collections import OrderedDict

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

import six

from agate.table import Table
from agate.data_types import Number, TypeTester
from agate.rows import Row
from agate import utils

def denormalize(table, key, property_column, value_column, default_value, column_types):
    """
    See :meth:`.Table.denormalize`.
    """
    if key is None:
        key = []
    elif not utils.issequence(key):
        key = [key]

    field_names = []
    row_data = OrderedDict()

    for row in table.rows:
        row_key = tuple(row[k] for k in key)

        if row_key not in row_data:
            row_data[row_key] = OrderedDict()

        f = six.text_type(row[property_column])
        v = row[value_column]

        if f not in field_names:
            field_names.append(f)

        row_data[row_key][f] = v

    if default_value == utils.default:
        if isinstance(table.columns[value_column].data_type, Number):
            default_value = Decimal(0)
        else:
            default_value = None

    new_column_names = key + field_names

    new_rows = []
    row_names = []

    for k, v in row_data.items():
        row = list(k)

        if len(k) == 1:
            row_names.append(k[0])
        else:
            row_names.append(k)

        for f in field_names:
            if f in v:
                row.append(v[f])
            else:
                row.append(default_value)

        new_rows.append(Row(row, new_column_names))

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
