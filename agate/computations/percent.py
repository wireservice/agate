#!/usr/bin/env python


from agate.aggregations.has_nulls import HasNulls
from agate.aggregations.sum import Sum
from agate.computations.base import Computation
from agate.data_types import Number
from agate.exceptions import DataTypeError
from agate.warns import warn_null_calculation


class Percent(Computation):
    """
    Calculate each values percentage of a total.

    :param column_name:
        The name of a column containing the :class:`.Number` values.
    :param total:
        If specified, the total value for each number to be divided into. By
        default, the :class:`.Sum` of the values in the column will be used.
    """
    def __init__(self, column_name, total=None):
        self._column_name = column_name
        self._total = total

    def get_computed_data_type(self, table):
        return Number()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Number):
            raise DataTypeError('Percent column must contain Number data.')
        if self._total is not None and self._total <= 0:
            raise DataTypeError('The total must be a positive number')

        # Throw a warning if there are nulls in there
        if HasNulls(self._column_name).run(table):
            warn_null_calculation(self, column)

    def prepare(self, table):
        """
        Compute the sum of the column to use as a total, if not provided by
        the user.
        """
        if self._total is None:
            self._total = table.aggregate(Sum(self._column_name))

            if self._total <= 0:
                raise DataTypeError('The sum of column values must be a positive number')

    def run(self, row):
        """
        :returns:
            :class:`decimal.Decimal`
        """
        value = row[self._column_name]

        if value is None:
            return None

        percent = value / self._total * 100

        return percent
