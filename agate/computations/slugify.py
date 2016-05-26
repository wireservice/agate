#!/usr/bin/env python

from agate.aggregations.has_nulls import HasNulls
from agate.computations.base import Computation
from agate.data_types import Text
from agate.exceptions import DataTypeError
from agate.utils import slugify


class Slugify(Computation):
    """
    Standardize the values in a Text column.

    :param column_name:
        The name of a column containing the :class:`.Text` values.
    :param ensure_unique:
        If True, any duplicate values will be appended with unique identifers.
        Defaults to False.
    """
    def __init__(self, column_name, ensure_unique=False, **kwargs):
        self._column_name = column_name
        self._ensure_unique = ensure_unique
        self._slug_args = kwargs

    def get_computed_data_type(self, table):
        return Text()

    def validate(self, table):
        column = table.columns[self._column_name]

        if not isinstance(column.data_type, Text):
            raise DataTypeError('Slugify column must contain Text data.')

        # Throw an error if there are nulls
        if HasNulls(self._column_name).run(table):
            raise ValueError('Slugify column cannot contain `None`.')

    def run(self, table):
        """
        :returns:
            :class:`string`
        """
        # Create a list new rows
        new_column = []

        # Loop through the existing rows
        for row in table.rows:
            # Pull the value
            new_column.append(row[self._column_name])

        # Pass out the list
        return slugify(new_column, ensure_unique=self._ensure_unique, **self._slug_args)
