#!/usr/bin/env python

from journalism.column import TextColumn, IntColumn, FloatColumn

COLUMN_TYPES = {
    str: TextColumn,
    unicode: TextColumn,
    int: IntColumn,
    float: FloatColumn
}

def transpose(table):
    """
    Transpose a list of lists.
    """
    return zip(*table)

class Table(dict):
    """
    A group of columns with names. Order doesn't matter.

    TODO: dedup column names
    """
    @staticmethod
    def get_column_type_for_data_type(data_type):
        """
        Get the Column type for a given native Python type.

        TODO: UnsupportedTypeError
        """
        return COLUMN_TYPES[data_type] 

    @staticmethod
    def from_rows(rows, column_types=[], column_names=[], validate=False):
        """
        Create a table from rows of data.
        """
        if not column_names:
            column_names = [unicode(d) for d in rows.pop(0)]

        table = {}
        columns = transpose(rows)

        for name, data, data_type in zip(column_names, columns, column_types):
            column_type = Table.get_column_type_for_data_type(data_type)
            table[name] = column_type(data, validate=validate)

        return Table(table)

    def from_csv(self):
        # TODO: use csvkit and convert columns into our types
        pass

    def to_csv(self):
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
