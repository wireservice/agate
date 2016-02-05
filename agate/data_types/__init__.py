#!/usr/bin/env python

"""
This module contains the :class:`.DataType` class and its subclasses. These
types define how data should be converted during the creation of a
:class:`.Table`.

A :class:`TypeTester` class is also included which be used to infer data
types from column data.
"""

from copy import copy

from agate.data_types.base import DEFAULT_NULL_VALUES, DataType  # noqa
from agate.data_types.boolean import Boolean
from agate.data_types.date import Date
from agate.data_types.date_time import DateTime
from agate.data_types.number import Number
from agate.data_types.text import Text
from agate.data_types.time_delta import TimeDelta
from agate.exceptions import CastError  # noqa


class TypeTester(object):
    """
    Infer data types for the columns in a given set of data.

    :param force:
        A dictionary where each key is a column name and each value is a
        :class:`.DataType` instance that overrides inference.
    :param limit:
        An optional limit on how many rows to evaluate before selecting the
        most likely type. Note that applying a limit may mean errors arise when
        the data is cast--if the guess is proved incorrect in further rows of
        data.
    :param types:
        A sequence of possible types to test against. This be used to specify
        what data formats you want to test against. For instance, you may want
        to exclude :class:`TimeDelta` from testing. It can also be used to pass
        options such as ``locale`` to :class:`.Number` or ``cast_nulls`` to
        :class:`.Text`. Take care in specifying the order of the list. It is
        the order they are tested in. :class:`.Text` should always be last.
    """
    def __init__(self, force={}, limit=None, types=None):
        self._force = force
        self._limit = limit

        if types:
            self._possible_types = types
        else:
            # In order of preference
            self._possible_types = [
                Boolean(),
                Number(),
                TimeDelta(),
                Date(),
                DateTime(),
                Text()
            ]

    def run(self, rows, column_names):
        """
        Apply type inference to the provided data and return an array of
        column types.

        :param rows:
            The data as a sequence of any sequences: tuples, lists, etc.
        """
        num_columns = len(column_names)
        hypotheses = [set(self._possible_types) for i in range(num_columns)]

        force_indices = [column_names.index(name) for name in self._force.keys()]

        if self._limit:
            sample_rows = rows[:self._limit]
        elif self._limit == 0:
            text = Text()
            return tuple([text] * num_columns)
        else:
            sample_rows = rows

        for row in sample_rows:
            for i in range(num_columns):
                if i in force_indices:
                    continue

                h = hypotheses[i]

                if len(h) == 1:
                    continue

                for column_type in copy(h):
                    if len(row) > i and not column_type.test(row[i]):
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

        return tuple(column_types)
