#!/usr/bin/env python
# pylint: disable=W0212

from collections import OrderedDict

import six


def to_dict(self, key, column_funcs=None):
    """
    Convert this table to an OrderedDict.

    :param key:
        May be either the name of a column from the this table containing
        unique values or a :class:`function` that takes a row and returns
        a unique value.
    :param column_funcs:
        If specified, a list of functions to apply to the columns in this
        table. See :meth:`.Table.to_json` for an example.
    """
    key_is_row_function = hasattr(key, '__call__')

    output = OrderedDict()

    for row in self._rows:
        if key_is_row_function:
            k = key(row)
        else:
            k = row[key]

        if k in output:
            raise ValueError('Value %s is not unique in the key column.' % six.text_type(k))

        if column_funcs:
            values = tuple(column_funcs[i](d) for i, d in enumerate(row))
        else:
            values = tuple(row)

        output[k] = OrderedDict(zip(row.keys(), values))

    return output

