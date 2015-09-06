#!/usr/bin/env python

import datetime

from dateutil.parser import parse
import six

from agate.column_types.base import *
from agate.exceptions import CastError

class DateTimeType(ColumnType):
    """
    Column type for :class:`DateTimeColumn`.
    """
    def __init__(self, datetime_format=None, null_values=DEFAULT_NULL_VALUES):
        super(DateTimeType, self).__init__(null_values=null_values)

        self.datetime_format = datetime_format

    def test(self, d):
        """
        Test, for purposes of type inference, if a string value could possibly
        be valid for this column type.
        """
        d = d.strip()

        if d.lower() in self.null_values:
            return True

        try:
            parse_result = parse(d)
        except:
            return False

        return True

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.datetime`.

        :param date_format: An optional :func:`datetime.strptime`
            format string for parsing datetimes in this column.
        :returns: :class:`datetime.datetime` or :code:`None`.
        """
        if isinstance(d, datetime.datetime) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        if self.datetime_format:
            return datetime.datetime.strptime(d, self.datetime_format)

        try:
            return parse(d)
        except:
            raise CastError('Can not parse value "%s" to as datetime for DateTimeColumn.' % d)

    def _create_column(self, table, index):
        from agate.columns import DateTimeColumn

        return DateTimeColumn(table, index)
