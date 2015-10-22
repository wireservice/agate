#!/usr/bin/env python

from agate.aggregations import *
from agate.data_types import *
from agate.computations import *
from agate.exceptions import *
from agate.mapped_sequence import MappedSequence
from agate.table import Table, allow_tableset_proxy
from agate.tableset import TableSet
from agate.warns import NullCalculationWarning, warn_null_calculation

def save():
    raise NotImplementedError
