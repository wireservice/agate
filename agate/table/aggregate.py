#!/usr/bin/env python

from agate import utils


def aggregate(table, aggregations):
    """
    See :meth:`.Table.aggregate`.
    """
    if utils.issequence(aggregations):
        results = []

        for agg in aggregations:
            agg.validate(table)

        for agg in aggregations:
            results.append(agg.run(table))

        return tuple(results)
    else:
        aggregations.validate(table)

        return aggregations.run(table)
