#!/usr/bin/env python

#: Default values which will be automatically cast to :code:`None`
DEFAULT_NULL_VALUES = ('', 'na', 'n/a', 'none', 'null', '.')

class ColumnType(object): #pragma: no cover
    """
    Base class for column data types.

    :param null_values: A sequence of values which should be cast to
        :code:`None` when encountered with this type.
    """
    def __init__(self, null_values=DEFAULT_NULL_VALUES):
        self.null_values = null_values

    def test(self, d):
        raise NotImplementedError

    def cast(self, d):
        raise NotImplementedError

    def _create_column(self, table, index):
        raise NotImplementedError
