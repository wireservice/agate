#!/usr/bin/env python

import sys

import six


def print_html(self, max_rows=20, max_columns=6, output=sys.stdout):
    """
    Print an HTML version of this table.

    :param max_rows:
        The maximum number of rows to display before truncating the data. By
        default all rows will be printed.
    :param max_columns:
        The maximum number of columns to display before truncating the data. By
        default all columns will be printed.
    :param output:
        A file-like object to print to. Defaults to :code:`sys.stdout`.
    """
    if max_rows is None:
        max_rows = len(self.rows)

    if max_columns is None:
        max_columns = len(self.columns)

    output.write('<table>')
    output.write('<thead>')
    output.write('<tr>')

    for i, col in enumerate(self.column_names):
        if i >= max_columns:
            break

        output.write('<th>')
        output.write(col)
        output.write('</th>')

    output.write('</tr>')
    output.write('</thead>')
    output.write('<tbody>')

    for i, row in enumerate(self.rows):
        if i >= max_rows:
            break

        output.write('<tr>')

        for i, col in enumerate(row):
            if i >= max_columns:
                break

            output.write('<td>')
            output.write(six.text_type(col))
            output.write('</td>')

        output.write('</tr>')

    output.write('</tbody>')
    output.write('</table>')
