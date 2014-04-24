#!/usr/bin/env python

import math

class NullComputationError(Exception):
    """
    Exception raised if an illogical computation is
    attempted on a Column containing nulls.
    """
    pass

class ColumnValidationError(Exception):
    """
    Exception raised in a column value can not be
    validated.

    TODO: details of what failed
    """
    pass

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
        return [d for d in self if d is not None]

class TextColumn(Column):
    """
    A column containing text data.
    """
    def max_length():
        pass

class SetColumn(Column):
    """
    A column containing "grouping" labels.
    """
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

    def unique(self):
        return list(set(self))

    def freq(self):
        # TODO: return dict or Table?
        pass

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

class Table(dict):
    """
    A group of columns with names. Order doesn't matter.
    """
    def __init__(self, columns=[]):
        # TODO: what if they pass somethign that isn't a column?
        pass

    def from_csv(self):
        # TODO: use csvkit and convert columns into our types
        pass

    def to_csv(self):
        pass

    def summarize(self):
        pass

    def count_rows(self):
        lengths = [len(c) for c in self]

        if lengths:
            return max(lengths)

        return 0

    def get_row(self, i):
        """
        Fetch a row of data from this table.
        """
        if i < 0:
            raise IndexError('Negative row numbers are not valid.')

        if i >= self.count_rows():
            raise IndexError('Row number exceeds the number of rows in the table.')

        row_data = [c[i] for c in self]

        return row_data

    def to_rows(self, serialize_dates=False):
        pass
