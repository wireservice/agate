#!/usr/bin/env python

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
    def from_rows(rows, column_types=[], column_names=[], validate=False):
        """
        Create a table from rows of data.

        TODO: validate column_types are all subclasses of Column.
        """
        if not column_names:
            column_names = [unicode(d) for d in rows.pop(0)]

        table = {}
        columns = transpose(rows)

        for name, data, column_type in zip(column_names, columns, column_types):
            table[name] = column_type(data, validate=validate)

        return Table(table)

    def to_rows(self, column_names=[], include_header=True):
        """
        Convert this table back to a sequence of rows.
        """
        if not column_names:
            column_names = self.keys()

        columns = [self[name] for name in column_names]
        rows = transpose(columns)

        if include_header:
            rows.insert(0, column_names)

        return rows

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

