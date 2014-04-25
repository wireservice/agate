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
        self.column_types = column_types

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def apply(self, column_name, operation):
        i = self.column_names.index(column_name)
        
        return operation(self.column_types[i], [r[i] for r in self.data])

    def filter(self, column_name, include=[]):
        """
        Filter a to only those rows where the column is in the
        include list.
        """
        i = self.column_names.index(column_name)

        rows = [row for row in self.data if row[i] in include]

        return Table(rows, self.column_types, self.column_names)

    def reject(self, column_name, exclude=[]):
        """
        Filter a to only those rows where the column is not in the
        exclude list.
        """
        i = self.column_names.index(column_name)

        rows = [row for row in self.data if row[i] not in exclude]

        return Table(rows, self.column_types, self.column_names)

    def aggregate(self, group_by, operations=[]):
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

        column_types = [self.column_types[i]]
        column_names = [group_by]

        for op_column in [op[0] for op in operations]:
            column_types.append(self.column_names.index(op_column))
            column_names.append(op_column)

        for name, group in groups.items():
            new_row = [name]

            for op_column, operation in operations:
                j = self.column_names.index(op_column)
                t = self.column_types[j]

                new_row.append(operation(t, [row[j] for row in group]))

            output.append(new_row)
        
        return Table(output, column_types, column_names) 

