#!/usr/bin/env python

from collections import Mapping

class Table(Mapping):
    """
    A group of columns with names.

    TODO: dedup column names
    """
    def __init__(self, rows, column_types=[], column_names=[], validate=False):
        """
        Create a table from rows of data.

        TODO: validate column_types are all subclasses of Column.
        """
        if not column_names:
            column_names = [unicode(d) for d in rows.pop(0)]

        self.column_names = column_names
        self.data = rows
        self.columns = []

        for name, column_type in zip(column_names, column_types):
            self.columns.append(column_type(self, name, validate=validate))

    def __getitem__(self, key):
        i = self.column_names.index(key)

        return self.columns[i]

    def __iter__(self):
        return iter(self.columns)

    def __len__(self):
        return len(self.columns)

    def _get_column_data(self, name):
        """
        Method for Column instances to access their data.
        """
        i = self.column_names.index(name)

        return [r[i] for r in self.data]

    def filter(self, column_name, include=[]):
        """
        Filter a to only those rows where the column is in the
        include list.
        """
        i = self.column_names.index(column_name)

        rows = filter(lambda r: r[i] in include, self.data)

        return Table(rows, [type(c) for c in self.columns], self.column_names)

    def reject(self, column_name, exclude=[]):
        """
        Filter a to only those rows where the column is not in the
        exclude list.
        """
        i = self.column_names.index(column_name)

        rows = filter(lambda r: r[i] not in exclude, self.data)

        return Table(rows, [type(c) for c in self.columns], self.column_names)

    def aggregate(self, group_by, operations={}):
        """
        Aggregate data by a specified group_by column.

        Operations is a dict of column names and operators.
        """
        i = self.column_names.index(group_by)

        groups = {}

        for row in self.data:
            group_name = row[i]

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append(row)

        output = []

        for name, group in groups:
            new_row = [name]

            for op_column, op_name in operations.items():
                j = self.column_names.index(op_column)

                new_row.append(op_name([row[j] for row in group]))

            output.append(new_row)
        
        return output

