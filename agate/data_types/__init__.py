#!/usr/bin/env python

"""
Data types define how data should be imported during the creation of a
:class:`.Table`.

If column types are not explicitly specified when a :class:`.Table` is created,
agate will attempt to guess them. The :class:`.TypeTester` class can be used to
control how types are guessed.
"""

from agate.data_types.base import DEFAULT_NULL_VALUES, DataType  # noqa
from agate.data_types.boolean import Boolean, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES  # noqa
from agate.data_types.date import Date  # noqa
from agate.data_types.date_time import DateTime  # noqa
from agate.data_types.number import Number  # noqa
from agate.data_types.text import Text  # noqa
from agate.data_types.time_delta import TimeDelta  # noqa
from agate.exceptions import CastError  # noqa
