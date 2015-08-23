#!/usr/bin/env python

import datetime

from dateutil.parser import parse

from journalism.columns.base import Column
from journalism.columns.operations.date_time import MinDateTime, MaxDateTime

class DateTimeColumn(Column):
    """
    A column containing :class:`datetime.datetime` data.
    """
    def __init__(self, *args, **kwargs):
        super(DateTimeColumn, self).__init__(*args, **kwargs)

        self.min = MinDateTime(self)
        self.max = MaxDateTime(self)
