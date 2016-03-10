#!/usr/bin/env python

from babel.numbers import format_decimal
import six

from agate.data_types import Number, Text
from agate import utils


def print_table(table, max_rows, max_columns, output, max_column_width, locale):
    """
    See :meth:`.Table.print_table`.
    """
    if max_rows is None:
        max_rows = len(table.rows)

    if max_columns is None:
        max_columns = len(table.columns)

    rows_truncated = max_rows < len(table.rows)
    columns_truncated = max_columns < len(table.column_names)

    column_names = list(table.column_names[:max_columns])

    if columns_truncated:
        column_names.append(utils.ELLIPSIS)

    widths = [len(n) for n in column_names]
    number_formatters = []
    formatted_data = []

    # Determine correct number of decimal places for each Number column
    for i, c in enumerate(table.columns):
        if i >= max_columns:
            break

        if isinstance(c.data_type, Number):
            max_places = utils.max_precision(c[:max_rows])
            number_formatters.append(utils.make_number_formatter(max_places))
        else:
            number_formatters.append(None)

    # Format data and display column widths
    for i, row in enumerate(table.rows):
        if i >= max_rows:
            break

        formatted_row = []

        for j, v in enumerate(row):
            if j >= max_columns:
                v = utils.ELLIPSIS
            elif v is None:
                v = ''
            elif number_formatters[j] is not None:
                v = format_decimal(
                    v,
                    format=number_formatters[j],
                    locale=locale or utils.LC_NUMERIC
                )
            else:
                v = six.text_type(v)

            if max_column_width is not None and len(v) > max_column_width:
                v = '%s...' % v[:max_column_width - 3]

            if len(v) > widths[j]:
                widths[j] = len(v)

            formatted_row.append(v)

            if j >= max_columns:
                break

        formatted_data.append(formatted_row)

    def _print_row(formatted_row):
        """
        Helper function that formats individual rows.
        """
        row_output = []

        for j, d in enumerate(formatted_row):
            # Text is left-justified, all other values are right-justified
            if isinstance(table.column_types[j], Text):
                row_output.append(' %s ' % d.ljust(widths[j]))
            else:
                row_output.append(' %s ' % d.rjust(widths[j]))

        line = utils.VERTICAL_LINE.join(row_output)

        return '%s %s %s' % (utils.VERTICAL_LINE, line, utils.VERTICAL_LINE)

    def write(line):
        output.write(line + '\n')

    # Dashes span each width with '+' character at intersection of
    # horizontal and vertical dividers.
    divider = '|--%s--|' % '-+-'.join('-' * w for w in widths)

    # Initial divider
    write(divider)

    # Headers
    write(_print_row(column_names))
    write(divider)

    # Rows
    for formatted_row in formatted_data:
        write(_print_row(formatted_row))

    # Row indicating data was truncated
    if rows_truncated:
        write(_print_row([utils.ELLIPSIS for n in column_names]))

    # Final divider
    write(divider)
