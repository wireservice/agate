import sys

from agate.data_types import Text
from agate.table import Table


def print_structure(self, max_rows=20, output=sys.stdout):
    """
    Print the keys and row counts of each table in the tableset.

    :param max_rows:
        The maximum number of rows to display before truncating the data.
        Defaults to 20.
    :param output:
        The output used to print the structure of the :class:`Table`.
    :returns:
        None
    """
    max_length = min(len(self.items()), max_rows)

    name_column = self.keys()[0:max_length]
    type_column = [str(len(table.rows)) for key, table in self.items()[0:max_length]]
    rows = zip(name_column, type_column)
    column_names = ['table', 'rows']
    text = Text()
    column_types = [text, text]

    table = Table(rows, column_names, column_types)

    return table.print_table(output=output, max_column_width=None)
