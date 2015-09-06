#!/usr/bin/env python

"""
This module contains the :class:`.Column` class and its various subclasses.
Each column is created from its associated :class:`.ColumnType` during the
creation of a :class:`.Table`. There is never any reason to create a column
by directly instantiating it.

Some columns implement custom behavior specific to their data type, when that
behavior does not naturally lend itself to becoming a :class:`.Aggregation` or
:class:`.Computation`. An example of this is :meth:`.NumberColumn.percentiles`,
which returns an array of 100 values. The output of this method can be applied
to create derivative values, such as in the :class:`.PercentileRank`
computation.
"""

from agate.columns.base import *
from agate.columns.boolean import *
from agate.columns.date_time import *
from agate.columns.number import *
from agate.columns.text import *
from agate.columns.time_delta import *
