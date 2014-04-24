#!/usr/bin/env python

import math

from journalism.exceptions import ColumnValidationError, NullComputationError

def no_null_computations(func):
    """
    Function decorator that prevents illogical computations
    on columns containing nulls.
    """
    def check(l, *args, **kwargs):
        if l.has_nulls():
            raise NullComputationError()

        return func(l)

    return check

class Column(list):
    """
    A list of data.
    """
    def __init__(self, data, validate=False):
        if validate:
            self.validate(data)

        super(Column, self).__init__(data)

    def __getitem__(self, key):
        """
        Return null for keys beyond the range of the column. This allows for columns to be of uneven length and still be merged into rows cleanly.
        """
        if key >= len(self):
            return None

        return list.__getitem__(self, key)

    @staticmethod
    def validate(data):
        """
        Validate that data is appropriate for this column type.

        Defaults to no-op.
        """
        return

    def has_nulls(self):
        """
        Check if this column contains nulls.
        """
        return None in self 

    def filter_nulls(self):
        """
        Return a copy of this column without nulls.
        """
        return type(self)([d for d in self if d is not None])

    def unique(self):
        """
        Return a copy of this column with only unique values.
        """
        return type(self)((set(self)))

    def freq(self):
        """
        Return the number of times each value appears in this column.
        """
        # TODO: return dict or Table?
        pass

class TextColumn(Column):
    """
    A column containing text data.
    """
    def max_length():
        # TODO
        pass

class NumberColumn(Column):
    """
    A column containing numeric data.
    """
    def sum(self):
        return sum(self.filter_nulls())

    def min(self):
        return min(self.filter_nulls())

    def max(self):
        return max(self.filter_nulls())

    @no_null_computations
    def mean(self):
        return float(self.sum() / len(self))

    @no_null_computations
    def median(self):
        length = len(self) 

        if length % 2 == 1:
            return self[((length + 1) / 2) - 1]
        else:
            a = self[(length / 2) - 1]
            b = self[length / 2]
        return (float(a + b)) / 2  

    def mode(self):
        # TODO
        pass

    @no_null_computations
    def stdev(self):
        return math.sqrt(sum(math.pow(v - self.mean(), 2) for v in self) / len(self))

class IntColumn(NumberColumn):
    """
    A column containing integer data.
    """
    @staticmethod
    def validate(data):
        for d in data:
            if not isinstance(d, int) and d is not None:
                raise ColumnValidationError()

class FloatColumn(NumberColumn):
    """
    A column containing float data.
    """
    pass

