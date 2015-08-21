#!/usr/bin/env python

import datetime

from dateutil.parser import parse

from journalism.columns.base import *

class DateTimeType(ColumnType):
    """
    Column type for :class:`DateTimeColumn`.
    """
    def __init__(self, datetime_format=None):
        self.datetime_format = datetime_format

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.datetime`.

        :param date_format: An optional :func:`datetime.strptime`
            format string for parsing datetimes in this column.
        :returns: :class`datetime.datetime` or :code:`None`.
        """
        if isinstance(d, datetime.datetime) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in NULL_VALUES:
                return None

        if self.datetime_format:
            return datetime.datetime.strptime(d, self.datetime_format)

        return parse(d)

    def _create_column(self, table, index):
        return DateTimeColumn(table, index)

    def _create_column_set(self, tableset, index):
        return DateTimeColumnSet(tableset, index)
        
class DateTimeColumn(Column):
    """
    A column containing :func:`datetime.datetime` data.
    """
    def min(self):
        """
        Compute the earliest datetime in this column.

        :returns: :class:`datetime.datetime`.
        """
        return min(self._data_without_nulls())

    def max(self):
        """
        Compute the latest datetime in this column.

        :returns: :class:`datetime.datetime`.
        """
        return max(self._data_without_nulls())

class DateTimeColumnSet(ColumnSet):
    """
    See :class:`ColumnSet` and :class:`DateTimeColumn`.
    """
    def __init__(self, *args, **kwargs):
        super(DateTimeColumnSet, self).__init__(*args, **kwargs)

        self.min = ColumnMethodProxy(self, 'min')
        self.max = ColumnMethodProxy(self, 'max')
