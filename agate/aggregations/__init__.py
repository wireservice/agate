#!/usr/bin/env python

"""
Aggregations create a new value by summarizing a :class:`.Column`. For
example, :class:`.Mean`, when applied to a column containing :class:`.Number`
data, returns a single :class:`decimal.Decimal` value which is the average of
all values in that column.

Aggregations can be applied to single columns using the :meth:`.Table.aggregate`
method. The result is a single value if a one aggregation was applied, or
a tuple of values if a sequence of aggregations was applied.

Aggregations can be applied to instances of :class:`.TableSet` using the
:meth:`.TableSet.aggregate` method. The result is a new :class:`.Table`
with a column for each aggregation and a row for each table in the set.
"""

from agate.aggregations.base import *

from agate.aggregations.all import *
from agate.aggregations.any import *
from agate.aggregations.count import *
from agate.aggregations.deciles import *
from agate.aggregations.has_nulls import *
from agate.aggregations.iqr import *
from agate.aggregations.mad import *
from agate.aggregations.max_length import *
from agate.aggregations.max_precision import *
from agate.aggregations.max import *
from agate.aggregations.mean import *
from agate.aggregations.median import *
from agate.aggregations.min import *
from agate.aggregations.mode import *
from agate.aggregations.percentiles import *
from agate.aggregations.quartiles import *
from agate.aggregations.quintiles import *
from agate.aggregations.stdev import *
from agate.aggregations.sum import *
from agate.aggregations.summary import *
from agate.aggregations.variance import *
