#!/usr/bin/env python

"""
Computations create a new value for each :class:`.Row` in a :class:`.Table`.
When used with :meth:`.Table.compute` these new values become a new column.
For instance, the :class:`.PercentChange` computation takes two column names as
arguments and computes the percentage change between them for each row.

There are a variety of basic computations, such as :class:`.Change` and
:class:`.Percent`. If none of these meet your needs you can use the
:class:`Formula` computation to apply an arbitrary function to the row.
If this still isn't flexible enough, it's simple to create a custom computation
class by inheriting from :class:`Computation`.
"""

from agate.computations.base import Computation  # noqa

from agate.computations.formula import Formula  # noqa
from agate.computations.change import Change  # noqa
from agate.computations.percent import Percent  # noqa
from agate.computations.percent_change import PercentChange  # noqa
from agate.computations.rank import Rank  # noqa
from agate.computations.percentile_rank import PercentileRank  # noqa
from agate.computations.slug import Slug  # noqa
