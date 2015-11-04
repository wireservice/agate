#!/usr/bin/env python

import datetime

import isodate
import parsedatetime
import six

from agate.data_types.base import DataType
from agate.exceptions import CastError

class DateTime(DataType):
    """
    Data type representing dates and times.

    :param datetime_format:
        A formatting string for :meth:`datetime.datetime.strptime` to use
        instead of using regex-based parsing.
    :param timezone:
        A `pytz <http://pytz.sourceforge.net/>`_ timezone to apply to each
        parsed date.
    """
    def __init__(self, datetime_format=None, timezone=None, **kwargs):
        super(DateTime, self).__init__(**kwargs)

        self.datetime_format = datetime_format
        self.timezone = timezone

        now = datetime.datetime.now()
        self._source_time = datetime.datetime(
            now.year, now.month, now.day, 0, 0, 0, 0, None
        )
        self._parser = parsedatetime.Calendar()

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.datetime`.

        :param date_format:
            An optional :func:`datetime.strptime` format string for parsing
            datetimes in this column.
        :returns:
            :class:`datetime.datetime` or :code:`None`.
        """
        if isinstance(d, datetime.datetime) or d is None:
            return d
        elif isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None
        else:
            raise CastError('Can not parse value "%s" as datetime.' % d)

        if self.datetime_format:
            try:
                return datetime.datetime.strptime(d, self.datetime_format)
            except:
                raise CastError('Value "%s" does not match date format.' % d)

        value, status = self._parser.parseDT(
            d,
            sourceTime=self._source_time,
            tzinfo=self.timezone
        )

        if status == 3:
            return value

        try:
            dt = isodate.parse_datetime(d)

            return dt
        except:
            pass

        raise CastError('Can not parse value "%s" as datetime.' % d)

    def csvify(self, d):
        if d is None:
            return None

        return d.isoformat()

    def jsonify(self, d):
        return self.csvify(d)
