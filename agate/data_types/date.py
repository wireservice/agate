#!/usr/bin/env python

from datetime import date, datetime, time

import isodate
import parsedatetime
import six

from agate.data_types.base import DataType
from agate.exceptions import CastError


ZERO_DT = datetime.combine(date.min, time.min)


class Date(DataType):
    """
    Data representing dates alone.

    :param date_format:
        A formatting string for :meth:`datetime.datetime.strptime` to use
        instead of using regex-based parsing.
    """
    def __init__(self, date_format=None, **kwargs):
        super(Date, self).__init__(**kwargs)

        self.date_format = date_format
        self.parser = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)

    def __getstate__(self):
        """
        Return state values to be pickled. Exclude _parser because parsedatetime
        cannot be pickled.
        """
        odict = self.__dict__.copy()
        del odict['parser']
        return odict

    def __setstate__(self, data):
        """
        Restore state from the unpickled state values. Set _parser to an instance
        of the parsedatetime Calendar class.
        """
        self.__dict__.update(data)
        self.parser = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.date`.

        :param date_format:
            An optional :func:`datetime.strptime` format string for parsing
            datetimes in this column.
        :returns:
            :class:`datetime.date` or :code:`None`.
        """
        if type(d) is date or d is None:
            return d
        elif isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None
        else:
            raise CastError('Can not parse value "%s" as date.' % d)

        if self.date_format:
            try:
                dt = datetime.strptime(d, self.date_format)
            except:
                raise CastError('Value "%s" does not match date format.' % d)

            return dt.date()

        value, ctx = self.parser.parseDT(d, sourceTime=ZERO_DT)

        if ctx.hasDate and not ctx.hasTime:
            return value.date()

        raise CastError('Can not parse value "%s" as date.' % d)

    def csvify(self, d):
        if d is None:
            return None

        return d.isoformat()

    def jsonify(self, d):
        return self.csvify(d)
