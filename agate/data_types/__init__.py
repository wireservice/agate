#!/usr/bin/env python

"""
This module contains the :class:`.DataType` class and its subclasses. These
types define how data should be converted during the creation of a
:class:`.Table`.

A :class:`TypeTester` class is also included which be used to infer data
types from column data.
"""

from copy import copy

from agate.data_types.base import DataType
from agate.data_types.boolean import Boolean
from agate.data_types.date import Date
from agate.data_types.date_time import DateTime
from agate.data_types.number import Number
from agate.data_types.text import Text
from agate.data_types.time_delta import TimeDelta

class TypeTester(object):
    """
    Infer data types for the columns in a given set of data.

    :param force: A dictionary where each key is a column name and each
        value is a :class:`.DataType` instance that overrides inference.
    :param locale: A locale to use when evaluating the types of data. See
        :class:`.Number`.
    """
    def __init__(self, force={}, locale='en_US'):
        self._force = force

        # In order of preference
        self._possible_types =[
            Boolean(),
            Number(locale=locale),
            TimeDelta(),
            DateTime(),
            Date(),
            Text()
        ]

    def run(self, rows, column_names):
        """
        Apply inference to the provided data and return an array of
        :code:`(column_name, column_type)` tuples suitable as an argument to
        :class:`.Table`.

        :param rows: The data as a sequence of any sequences: tuples, lists,
            etc.
        :param column_names: A sequence of column names.
        """
        num_columns = len(column_names)
        hypotheses = [set(self._possible_types) for i in range(num_columns)]

        force_indices = [column_names.index(name) for name in self._force.keys()]

        for row in rows:
            for i in range(num_columns):
                if i in force_indices:
                    continue

                h = hypotheses[i]

                if len(h) == 1:
                    continue

                for column_type in copy(h):
                    if not column_type.test(row[i]):
                        h.remove(column_type)

        column_types = []

        for i in range(num_columns):
            if i in force_indices:
                column_types.append(self._force[column_names[i]])
                continue

            h = hypotheses[i]

            # Select in prefer order
            for t in self._possible_types:
                if t in h:
                    column_types.append(t)
                    break

        return tuple(zip(column_names, column_types))
