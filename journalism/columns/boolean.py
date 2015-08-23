#!/usr/bin/env python

from journalism.columns.base import Column
from journalism.columns.operations.boolean import AnyBoolean, AllBoolean

class BooleanColumn(Column):
    """
    A column containing :class:`bool` data.
    """
    def __init__(self, *args, **kwargs):
        super(BooleanColumn, self).__init__(*args, **kwargs)

        self.any = AnyBoolean(self)
        self.all = AllBoolean(self)
