#!/usr/bin/env python

import six

from agate.aggregations import Count
from agate import utils


def pivot(table, key, pivot, aggregation, computation, default_value, key_name):
    """
    See :meth:`.Table.pivot`.
    """
    if key is None:
        key = []
    elif not utils.issequence(key):
        key = [key]
    elif key_name:
        raise ValueError('key_name is not a valid argument when key is a sequence.')

    if aggregation is None:
        aggregation = Count()

    groups = table

    for k in key:
        groups = groups.group_by(k, key_name=key_name)

    aggregation_name = six.text_type(aggregation)
    computation_name = six.text_type(computation) if computation else None

    def apply_computation(table):
        table = table.compute([
            (computation_name, computation)
        ])

        table = table.exclude([aggregation_name])

        return table

    if pivot is not None:
        groups = groups.group_by(pivot)

        column_type = aggregation.get_aggregate_data_type(groups)

        table = groups.aggregate([
            (aggregation_name, aggregation)
        ])

        pivot_count = len(set(table.columns[pivot].values()))

        if computation is not None:
            column_types = computation.get_computed_data_type(table)
            table = apply_computation(table)

        column_types = [column_type] * pivot_count

        table = table.denormalize(key, pivot, computation_name or aggregation_name, default_value=default_value, column_types=column_types)
    else:
        table = groups.aggregate([
            (aggregation_name, aggregation)
        ])

        if computation:
            table = apply_computation(table)

    return table
