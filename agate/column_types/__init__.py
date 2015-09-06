#!/usr/bin/env python

"""
This module contains the :class:`ColumnType` class and its subclasses. These
types define how data should be converted during the creation of a
:class:`.Table`. Each subclass of :class:`ColumnType` is associated with a
subclass of :class:`.Column`. For instance, specifying that data is of
:class:`NumberType` will cause a :class:`.NumberColumn` to be created on the
table.
"""

from agate.column_types.base import *
from agate.column_types.boolean import *
from agate.column_types.date_time import *
from agate.column_types.number import *
from agate.column_types.text import *
from agate.column_types.time_delta import *
