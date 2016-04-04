#!/usr/bin/env python

from agate.parallel import parallelize
from agate.rows import Row
from agate import utils


@utils.allow_tableset_proxy
def compute(self, computations, replace=False):
    """
    Create a new table by applying one or more :class:`.Computation` instances
    to each row.

    :param computations:
        A sequence of pairs of new column names and :class:`.Computation`
        instances.
    :param replace:
        If :code:`True` then new column names can match existing names, and
        those columns will be replaced with the computed data.
    :returns:
        A new :class:`.Table`.
    """
    column_names = list(self.column_names)
    column_types = list(self.column_types)

    for new_column_name, computation in computations:
        new_column_type = computation.get_computed_data_type(self)

        if new_column_name in column_names:
            if not replace:
                raise ValueError('New column name "%s" already exists. Specify replace=True to replace with computed data.')

            i = column_names.index(new_column_name)
            column_types[i] = new_column_type
        else:
            column_names.append(new_column_name)
            column_types.append(new_column_type)

        computation.validate(self)

    for new_column_name, computation in computations:
        computation.prepare(self)

    new_rows = parallelize(_compute, self.rows, computations, column_names, replace)

    return self._fork(new_rows, column_names, column_types)


def _compute(rows, computations, column_names, replace):
    """
    Threadable implementation of compute (a.k.a. map).
    """
    new_rows = []
    new_column_names = tuple(n for n, c in computations)

    for row in rows:
        new_values = tuple(c.run(row) for n, c in computations)

        # Slow version if using replace
        if replace:
            values = []

            for j, column_name in enumerate(column_names):
                if column_name in new_column_names:
                    k = new_column_names.index(column_name)
                    values.append(new_values[k])
                else:
                    values.append(row[j])
        # Faster version if not using replace
        else:
            values = row.values() + new_values

        new_rows.append(Row(values, column_names))

    return new_rows
