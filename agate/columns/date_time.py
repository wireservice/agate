#!/usr/bin/env python

import datetime

from dateutil.parser import parse

from agate.columns.base import Column

class DateTimeColumn(Column):
    """
    A column containing :class:`datetime.datetime` data.
    """
    def __init__(self, *args, **kwargs):
        pass
