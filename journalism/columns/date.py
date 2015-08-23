#!/usr/bin/env python

import datetime

from journalism.columns.base import Column
from journalism.columns.operations.date import MinDate, MaxDate

class DateColumn(Column):
    """
    A column containing :class:`datetime.date` data.
    """
    def __init__(self, *args, **kwargs):
        super(DateColumn, self).__init__(*args, **kwargs)

        self.min = MinDate(self)
        self.max = MaxDate(self)
