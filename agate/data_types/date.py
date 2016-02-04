#!/usr/bin/env python

import datetime

import isodate
import parsedatetime
import six

from agate.data_types.base import DataType
from agate.exceptions import CastError


class Date(DataType):
    """
    Data type representing dates only.

    :param date_format:
        A formatting string for :meth:`datetime.datetime.strptime` to use
        instead of using regex-based parsing.
    """
    def __init__(self, date_format=None, **kwargs):
        super(Date, self).__init__(**kwargs)

        self.date_format = date_format
        self.parser = parsedatetime.Calendar()

    def __getstate__(self):
        """
        Return state values to be pickled. Exclude _parser because parsedatetime
        cannot be pickled.
        """
        odict = self.__dict__.copy()
        del odict['parser']
        return odict

    def __setstate__(self, dict):
        """
        Restore state from the unpickled state values. Set _parser to an instance
        of the parsedatetime Calendar class.
        """
        self.__dict__.update(dict)
        self.parser = parsedatetime.Calendar()

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.date`.

        :param date_format:
            An optional :func:`datetime.strptime` format string for parsing
            datetimes in this column.
        :returns:
            :class:`datetime.date` or :code:`None`.
        """
        if type(d) is datetime.date or d is None:
            return d
        elif isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None
        else:
            raise CastError('Can not parse value "%s" as date.' % d)

        if self.date_format:
            try:
                dt = datetime.datetime.strptime(d, self.date_format)
            except:
                raise CastError('Value "%s" does not match date format.' % d)

            return dt.date()

        zero = datetime.datetime.combine(datetime.date.min, datetime.time.min)

        value, status = self.parser.parseDT(d, sourceTime=zero)

        if status == 1:
            if value.time() != datetime.time.min:
                raise CastError('Value "%s" is datetime, not date.' % d)

            return value.date()

        try:
            dt = isodate.parse_date(d)

            try:
                dt = isodate.parse_datetime(d)
            except:
                return dt
        except:
            pass

        raise CastError('Can not parse value "%s" as date.' % d)

    def csvify(self, d):
        if d is None:
            return None

        return d.isoformat()

    def jsonify(self, d):
        return self.csvify(d)
