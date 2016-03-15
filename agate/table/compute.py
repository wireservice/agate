#!/usr/bin/env python

from copy import copy

from agate.rows import Row
from agate import utils


@utils.allow_tableset_proxy
def compute(self, computations):
    """
    Create a new table by applying one or more :class:`.Computation` instances
    to each row.

    :param computations:
        A sequence of pairs of new column names and :class:`.Computation`
        instances.
    :returns:
        A new :class:`.Table`.
    """
    column_names = list(copy(self.column_names))
    column_types = list(copy(self.column_types))

    for new_column_name, computation in computations:
        column_names.append(new_column_name)
        column_types.append(computation.get_computed_data_type(self))

        computation.validate(self)

    new_columns = tuple(c.run(self) for n, c in computations)
    new_rows = []

    for i, row in enumerate(self.rows):
        values = tuple(row) + tuple(c[i] for c in new_columns)
        new_rows.append(Row(values, column_names))

    return self._fork(new_rows, column_names, column_types)
