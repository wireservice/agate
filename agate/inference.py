#!/usr/bin/env python

from copy import copy

from agate.column_types import *
from agate.exceptions import *

def infer_types(rows, force={}):
    """
    Infer types for the columns in a given set of data.

    :param force: A dictionary where each key is a column name and each value
        is a :class:`.ColumnType` that overrides inference.
    """
    # In order of preference
    possible_types = [
        BooleanType,
        NumberType,
        TimeDeltaType,
        DateTimeType,
        TextType
    ]

    num_columns = len(rows[0])
    hypotheses = [set(possible_types) for i in range(num_columns)]

    for row in rows:
        for i in range(num_columns):
            h = hypotheses[i]

            if len(h) == 1:
                continue

            for column_type in copy(h):
                if not column_type.test(row[i]):
                    h.remove(column_type)

    column_types = []

    for i in range(num_columns):
        h = hypotheses[i]

        # Select in prefer order
        for t in possible_types:
            if t in h:
                column_types.append(t)
                break

    return column_types
