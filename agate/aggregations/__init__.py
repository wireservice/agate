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

from agate.aggregations.base import Aggregation  # noqa

from agate.aggregations.all import All  # noqa
from agate.aggregations.any import Any  # noqa
from agate.aggregations.count import Count  # noqa
from agate.aggregations.deciles import Deciles  # noqa
from agate.aggregations.first import First  # noqa
from agate.aggregations.has_nulls import HasNulls  # noqa
from agate.aggregations.iqr import IQR  # noqa
from agate.aggregations.mad import MAD  # noqa
from agate.aggregations.max_length import MaxLength  # noqa
from agate.aggregations.max_precision import MaxPrecision  # noqa
from agate.aggregations.max import Max  # noqa
from agate.aggregations.mean import Mean  # noqa
from agate.aggregations.median import Median  # noqa
from agate.aggregations.min import Min  # noqa
from agate.aggregations.mode import Mode  # noqa
from agate.aggregations.percentiles import Percentiles  # noqa
from agate.aggregations.quartiles import Quartiles  # noqa
from agate.aggregations.quintiles import Quintiles  # noqa
from agate.aggregations.stdev import StDev, PopulationStDev  # noqa
from agate.aggregations.sum import Sum  # noqa
from agate.aggregations.summary import Summary  # noqa
from agate.aggregations.variance import Variance, PopulationVariance  # noqa
