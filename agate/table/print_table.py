#!/usr/bin/env python

import sys

from babel.numbers import format_decimal
import six

from agate.data_types import Number, Text
from agate import utils


def print_table(self, max_rows=20, max_columns=6, output=sys.stdout, max_column_width=20, locale=None):
    """
    Print a text-based view of the data in this table..

    :param max_rows:
        The maximum number of rows to display before truncating the data. This
        defaults to :code:`20` to prevent accidental printing of the entire
        table. Pass :code:`None` to disable the limit.
    :param max_columns:
        The maximum number of columns to display before truncating the data.
        This defaults to :code:`6` to prevent wrapping in most cases. Pass
        :code:`None` to disable the limit.
    :param output:
        A file-like object to print to. Defaults to :code:`sys.stdout`.
    :param max_column_width:
        Truncate all columns to at most this width. The remainder will be
        replaced with ellipsis.
    :param locale:
        Provide a locale you would like to be used to format the output.
        By default it will use the system's setting.
    """
    if max_rows is None:
        max_rows = len(self.rows)

    if max_columns is None:
        max_columns = len(self.columns)

    rows_truncated = max_rows < len(self.rows)
    columns_truncated = max_columns < len(self.column_names)

    column_names = list(self.column_names[:max_columns])

    if columns_truncated:
        column_names.append(utils.ELLIPSIS)

    widths = [len(n) for n in column_names]
    number_formatters = []
    formatted_data = []

    # Determine correct number of decimal places for each Number column
    for i, c in enumerate(self.columns):
        if i >= max_columns:
            break

        if isinstance(c.data_type, Number):
            max_places = utils.max_precision(c[:max_rows])
            number_formatters.append(utils.make_number_formatter(max_places))
        else:
            number_formatters.append(None)

    # Format data and display column widths
    for i, row in enumerate(self.rows):
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
            if isinstance(self.column_types[j], Text):
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
