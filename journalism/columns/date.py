#!/usr/bin/env python

import datetime

from dateutil.parser import parse

from journalism.columns.base import *

class DateType(ColumnType):
    """
    Column type for :class:`DateColumn`.
    """
    def __init__(self, date_format=None):
        self.date_format = date_format

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.date`.

        :param date_format: An optional :func:`datetime.strptime`
            format string for parsing dates in this column.
        :returns: :class`datetime.date` or :code:`None`.
        """
        if isinstance(d, datetime.date) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in NULL_VALUES:
                return None

        if self.date_format:
            return datetime.datetime.strptime(d, self.date_format).date()

        return parse(d).date()

    def _create_column(self, table, index):
        return DateColumn(table, index)

    def _create_column_set(self, tableset, index):
        return DateColumnSet(tableset, index)

class DateColumn(Column):
    """
    A column containing :func:`datetime.date` data.
    """
    def min(self):
        """
        Compute the earliest date in this column.

        :returns: :class:`datetime.date`.
        """
        return min(self._data_without_nulls())

    def max(self):
        """
        Compute the latest date in this column.

        :returns: :class:`datetime.date`.
        """
        return max(self._data_without_nulls())

class DateColumnSet(ColumnSet):
    """
    See :class:`ColumnSet` and :class:`DateColumn`.
    """
    def __init__(self, *args, **kwargs):
        super(DateColumnSet, self).__init__(*args, **kwargs)

        self.min = ColumnMethodProxy(self, 'min')
        self.max = ColumnMethodProxy(self, 'max')
