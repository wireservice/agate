#!/usr/bin/env python

import sys

from six.moves import zip   # pylint: disable=W0622

from agate.data_types import Text


def print_structure(self, output=sys.stdout):
    """
    Print this table's column names and types as a plain-text table.

    :param output:
        The output to print to.
    """
    from agate.table import Table

    name_column = [n for n in self.column_names]
    type_column = [t.__class__.__name__ for t in self.column_types]
    rows = tuple(zip(name_column, type_column))
    column_names = ['column', 'data_type']
    text = Text()
    column_types = [text, text]

    table = Table(rows, column_names, column_types)

    return table.print_table(output=output, max_column_width=None)
