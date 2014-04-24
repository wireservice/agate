#!/usr/bin/env python

from collections import Sequence
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

class Column(Sequence):
    """
    A proxy to a column with a Table.
    """
    def __init__(self, table, name, validate=False):
        self.table = table
        self.name = name

        print validate

        if validate:
            self.validate()

    def _get_data(self):
        """
        Get column data from the parent Table.
        """
        return self.table._get_column_data(self.name) 

    def __getitem__(self, key):
        """
        Return null for keys beyond the range of the column. This allows for columns to be of uneven length and still be merged into rows cleanly.
        """
        return self._get_data()[key]

    def __len__(self):
        return len(self._get_data())

    def validate(self, data):
        """
        Validate that data is appropriate for this column type.

        Defaults to no-op.
        """
        raise NotImplementedError()

    def has_nulls(self):
        """
        Check if this column contains nulls.
        """
        return None in self._get_data() 

    def _filter_nulls(self):
        return [d for d in self._get_data() if d is not None]

    def unique(self):
        """
        Return a copy of this column with only unique values.
        """
        return set(self._get_data())

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
    def validate(self):
        for d in self._get_data():
            if not isinstance(d, basestring) and d is not None:
                raise ColumnValidationError()

    def max_length():
        # TODO
        pass

class NumberColumn(Column):
    """
    A column containing numeric data.
    """
    def sum(self):
        return sum(self._filter_nulls())

    def min(self):
        return min(self._filter_nulls())

    def max(self):
        return max(self._filter_nulls())

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

    @no_null_computations
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
    print 'validate'
    def validate(self):
        for d in self._get_data():
            if not isinstance(d, int) and d is not None:
                raise ColumnValidationError()

class FloatColumn(NumberColumn):
    """
    A column containing float data.
    """
    def validate(self):
        for d in self._get_data():
            if not isinstance(d, float) and d is not None:
                raise ColumnValidationError()

