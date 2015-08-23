#!/usr/bin/env python

import six

from journalism.columns.base import Column
from journalism.columns.operations.text import MaxLength

class TextColumn(Column):
    """
    A column containing unicode/string data.
    """
    def __init__(self, *args, **kwargs):
        super(TextColumn, self).__init__(*args, **kwargs)

        self.max_length = MaxLength(self)
