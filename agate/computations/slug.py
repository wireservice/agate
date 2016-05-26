#!/usr/bin/env python

from agate.aggregations.has_nulls import HasNulls
from agate.computations.base import Computation
from agate.data_types import Text
from agate.exceptions import DataTypeError
from agate.utils import slugify


class Slug(Computation):
    """
    Convert text values into a column into slugs.

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
            raise DataTypeError('Slug column must contain Text data.')

        if HasNulls(self._column_name).run(table):
            raise ValueError('Slug column cannot contain `None`.')

    def run(self, table):
        """
        :returns:
            :class:`string`
        """
        new_column = []

        for row in table.rows:
            new_column.append(row[self._column_name])

        return slugify(new_column, ensure_unique=self._ensure_unique, **self._slug_args)
