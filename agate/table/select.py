#!/usr/bin/env python

from agate.fast import parallelize
from agate.rows import Row
from agate import utils


@utils.allow_tableset_proxy
def select(self, key):
    """
    Create a new table with only the specified columns.

    :param key:
        Either the name of a single column to include or a sequence of such
        names.
    :returns:
        A new :class:`.Table`.
    """
    if not utils.issequence(key):
        key = [key]

    column_types = [self.columns[name].data_type for name in key]

    new_rows = parallelize(_select, self._rows, key)

    return self._fork(new_rows, key, column_types)

def _select(rows, key):
    new_rows = []

    for row in rows:
        new_rows.append(Row(tuple(row[n] for n in key), key))

    return new_rows
