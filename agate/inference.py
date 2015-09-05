#!/usr/bin/env python

from copy import copy

from agate.column_types import *
from agate.exceptions import *

def infer_types(rows, overrides={}):
    possible_types = {
        'boolean': BooleanType(),
        'date': DateType(),
        'datetime': DateTimeType(),
        'timedelta': TimeDeltaType(),
        'number': NumberType(),
        'text': TextType()
    }

    num_columns = len(rows[0])
    hypotheses = [set(possible_types.values()) for i in range(num_columns)]

    for row in rows:
        for i in range(num_columns):
            h = hypotheses[i]

            if len(h) == 1:
                continue

            for column_type in copy(h):
                try:
                    column_type.cast(row[i])
                except CastError:
                    h.remove(column_type)

    preference_order = [
        possible_types['boolean'],
        possible_types['number'],
        possible_types['timedelta'],
        possible_types['datetime'],
        # possible_types['date'],
        possible_types['text']
    ]

    column_types = []

    for i in range(num_columns):
        h = hypotheses[i]

        for t in preference_order:
            if t in h:
                column_types.append(t)
                break
        else:
            column_types.append(None)

    return column_types
