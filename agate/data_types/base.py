#!/usr/bin/env python

#: Default values which will be automatically cast to :code:`None`
DEFAULT_NULL_VALUES = ('', 'na', 'n/a', 'none', 'null', '.')

class DataType(object): #pragma: no cover
    """
    Base class for data types.

    :param null_values: A sequence of values which should be cast to
        :code:`None` when encountered with this type.
    """
    def __init__(self, null_values=DEFAULT_NULL_VALUES):
        self.null_values = null_values

    def test(self, d):
        """
        Test if a given string value could possibly be an instance of this
        data type.
        """
        raise NotImplementedError

    def cast(self, d):
        """
        Coerce a given string value into this column's data type.
        """
        raise NotImplementedError
