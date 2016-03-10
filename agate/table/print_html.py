#!/usr/bin/env python

import six


def print_html(table, max_rows, max_columns, output):
    """
    See :meth:`.Table.print_html`.
    """
    if max_rows is None:
        max_rows = len(table.rows)

    if max_columns is None:
        max_columns = len(table.columns)

    output.write('<table>')
    output.write('<thead>')
    output.write('<tr>')

    for i, col in enumerate(table.column_names):
        if i >= max_columns:
            break

        output.write('<th>')
        output.write(col)
        output.write('</th>')

    output.write('</tr>')
    output.write('</thead>')
    output.write('<tbody>')

    for i, row in enumerate(table.rows):
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
