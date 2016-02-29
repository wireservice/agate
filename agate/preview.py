#!/usr/bin/env python
# -*- coding: utf8 -*-

from collections import OrderedDict

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

import sys

from babel.core import default_locale
from babel.numbers import format_decimal
import six
from six.moves import zip

from agate.aggregations import Min, Max
from agate.data_types import Number, Text
from agate.exceptions import DataTypeError
from agate.utils import max_precision, make_number_formatter, round_limits

#: Character to render for horizontal lines
HORIZONTAL_LINE = u'-'

#: Character to render for vertical lines
VERTICAL_LINE = u'|'

#: Character to render for bar chart units
BAR_MARK = u'░'

#: Printable character to render for bar chart units
PRINTABLE_BAR_MARK = u':'

#: Character to render for zero line units
ZERO_MARK = u'▓'

#: Printable character to render for zero line units
PRINTABLE_ZERO_MARK = u'|'

#: Character to render for axis ticks
TICK_MARK = u'+'

#: Characters to render for ellipsis
ELLIPSIS = u'...'

# Get the default locale for number formatting
# (Falls back to English to work around a Windows bug)
LC_NUMERIC = default_locale('LC_NUMERIC') or 'en_US'


def print_table(table, max_rows=None, max_columns=None, output=sys.stdout, max_column_width=None, locale=None):
    """
    See :meth:`.Table.print_table` for documentation.
    """
    if max_rows is None:
        max_rows = len(table.rows)

    if max_columns is None:
        max_columns = len(table.columns)

    rows_truncated = max_rows < len(table.rows)
    columns_truncated = max_columns < len(table.column_names)

    column_names = list(table.column_names[:max_columns])

    if columns_truncated:
        column_names.append(ELLIPSIS)

    widths = [len(n) for n in column_names]
    number_formatters = []
    formatted_data = []

    # Determine correct number of decimal places for each Number column
    for i, c in enumerate(table.columns):
        if i >= max_columns:
            break

        if isinstance(c.data_type, Number):
            max_places = max_precision(c[:max_rows])
            number_formatters.append(make_number_formatter(max_places))
        else:
            number_formatters.append(None)

    # Format data and display column widths
    for i, row in enumerate(table.rows):
        if i >= max_rows:
            break

        formatted_row = []

        for j, v in enumerate(row):
            if j >= max_columns:
                v = ELLIPSIS
            elif v is None:
                v = ''
            elif number_formatters[j] is not None:
                v = format_decimal(
                    v,
                    format=number_formatters[j],
                    locale=locale or LC_NUMERIC
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

        line = VERTICAL_LINE.join(row_output)

        return '%s %s %s' % (VERTICAL_LINE, line, VERTICAL_LINE)

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
        write(_print_row([ELLIPSIS for n in column_names]))

    # Final divider
    write(divider)


def print_html(table, max_rows=None, max_columns=None, output=sys.stdout):
    """
    See :meth:`.Table.print_html` for documentation.
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


def print_bars(table, label_column_name, value_column_name, domain=None, width=120, output=sys.stdout, printable=False):
    """
    Print a bar chart representation of two columns.
    """
    y_label = label_column_name
    label_column = table.columns[label_column_name]

    # if not isinstance(label_column.data_type, Text):
    #     raise ValueError('Only Text data is supported for bar chart labels.')

    x_label = value_column_name
    value_column = table.columns[value_column_name]

    if not isinstance(value_column.data_type, Number):
        raise DataTypeError('Only Number data is supported for bar chart values.')

    output = output
    width = width

    # Format numbers
    decimal_places = max_precision(value_column)
    value_formatter = make_number_formatter(decimal_places)

    formatted_labels = []

    for label in label_column:
        formatted_labels.append(six.text_type(label))

    formatted_values = []

    for value in value_column:
        formatted_values.append(format_decimal(
                value,
                format=value_formatter,
                locale=LC_NUMERIC
            )
        )

    max_label_width = max(max([len(l) for l in formatted_labels]), len(y_label))
    max_value_width = max(max([len(v) for v in formatted_values]), len(x_label))

    plot_width = width - (max_label_width + max_value_width + 2)

    min_value = Min(value_column_name).run(table)
    max_value = Max(value_column_name).run(table)

    # Calculate dimensions
    if domain:
        x_min = Decimal(domain[0])
        x_max = Decimal(domain[1])

        if min_value < x_min or max_value > x_max:
            raise ValueError('Column contains values outside specified domain')
    else:
        x_min, x_max = round_limits(min_value, max_value)

    # All positive
    if x_min >= 0:
        x_min = Decimal('0')
        plot_negative_width = 0
        zero_line = 0
        plot_positive_width = plot_width - 1
    # All negative
    elif x_max <= 0:
        x_max = Decimal('0')
        plot_negative_width = plot_width - 1
        zero_line = plot_width - 1
        plot_positive_width = 0
    # Mixed signs
    else:
        spread = x_max - x_min
        negative_portion = (x_min.copy_abs() / spread)

        # Subtract one for zero line
        plot_negative_width = int(((plot_width - 1) * negative_portion).to_integral_value())
        zero_line = plot_negative_width
        plot_positive_width = plot_width - (plot_negative_width + 1)

    def project(value):
        if value >= 0:
            return plot_negative_width + int((plot_positive_width * (value / x_max)).to_integral_value())
        else:
            return plot_negative_width - int((plot_negative_width * (value / x_min)).to_integral_value())

    # Calculate ticks
    ticks = OrderedDict()

    # First tick
    ticks[0] = x_min
    ticks[plot_width - 1] = x_max

    tick_fractions = [Decimal('0.25'), Decimal('0.5'), Decimal('0.75')]

    # All positive
    if x_min >= 0:
        for fraction in tick_fractions:
            value = x_max * fraction
            ticks[project(value)] = value
    # All negative
    elif x_max <= 0:
        for fraction in tick_fractions:
            value = x_min * fraction
            ticks[project(value)] = value
    # Mixed signs
    else:
        # Zero tick
        ticks[zero_line] = Decimal('0')

        # Halfway between min and 0
        value = x_min * Decimal('0.5')
        ticks[project(value)] = value

        # Halfway between 0 and max
        value = x_max * Decimal('0.5')
        ticks[project(value)] = value

    decimal_places = max_precision(ticks.values())
    tick_formatter = make_number_formatter(decimal_places)

    ticks_formatted = OrderedDict()

    for k, v in ticks.items():
        ticks_formatted[k] = format_decimal(
            v,
            format=tick_formatter,
            locale=LC_NUMERIC
        )

    def write(line):
        output.write(line + '\n')

    # Chart top
    top_line = u'%s %s' % (y_label.ljust(max_label_width), x_label.rjust(max_value_width))
    write(top_line)

    if printable:
        bar_mark = PRINTABLE_BAR_MARK
        zero_mark = PRINTABLE_ZERO_MARK
    else:
        bar_mark = BAR_MARK
        zero_mark = ZERO_MARK

    # Bars
    for i, label in enumerate(formatted_labels):
        value = value_column[i]

        if value == 0:
            bar_width = 0
        elif value > 0:
            bar_width = project(value) - plot_negative_width
        elif value < 0:
            bar_width = plot_negative_width - project(value)

        label_text = label.ljust(max_label_width)
        value_text = formatted_values[i].rjust(max_value_width)

        bar = bar_mark * bar_width

        if value >= 0:
            gap = (u' ' * plot_negative_width)

            # All positive
            if x_min <= 0:
                bar = gap + zero_mark + bar
            else:
                bar = bar + gap + zero_mark
        else:
            bar = u' ' * (plot_negative_width - bar_width) + bar

            # All negative or mixed signs
            if x_max > value:
                bar = bar + zero_mark

        bar = bar.ljust(plot_width)

        write('%s %s %s' % (label_text, value_text, bar))

    # Axis & ticks
    axis = HORIZONTAL_LINE * plot_width
    tick_text = u' ' * width

    for i, (tick, label) in enumerate(ticks_formatted.items()):
        # First tick
        if tick == 0:
            offset = 0
        # Last tick
        elif tick == plot_width - 1:
            offset = -(len(label) - 1)
        else:
            offset = int(-(len(label) / 2))

        pos = (width - plot_width) + tick + offset

        # Don't print intermediate ticks that would overlap
        if tick != 0 and tick != plot_width - 1:
            if tick_text[pos - 1:pos + len(label) + 1] != ' ' * (len(label) + 2):
                continue

        tick_text = tick_text[:pos] + label + tick_text[pos + len(label):]
        axis = axis[:tick] + TICK_MARK + axis[tick + 1:]

    write(axis.rjust(width))
    write(tick_text)


def print_structure(left_column, right_column, column_headers, output=sys.stdout):
    """
    See :meth:`.Table.print_structure` and :meth:`.TableSet.print_structure`
    for documentation.
    """
    def write(line):
        output.write(line + '\n')

    def _print_row(formatted_row):
        """
        Helper function that formats individual rows.

        :param formatted_row:
            A list of strings representing the cells of a row.
        :returns:
            A string representing the final row of the table.
        """
        line = VERTICAL_LINE.join(formatted_row)

        return '%s %s %s' % (VERTICAL_LINE, line, VERTICAL_LINE)

    def _max_width(values, column_name):
        """
        Return the width necessary to contain the longest column value.

        :param values:
            The values in a column.
        :param name:
            The name of the column.
        :returns:
            The length of the longest string in the column.
        """
        return max(max(len(value) for value in values), len(column_name))

    left_column_width = _max_width(left_column, column_headers[0])
    right_column_width = _max_width(right_column, column_headers[1])

    header = [
        (' ' + column_headers[0] + ' ').ljust(left_column_width + 2),
        (' ' + column_headers[1] + ' ').ljust(right_column_width + 2)
    ]

    divider = '|--%s--|' % '-+-'.join('-' * w for w in (left_column_width, right_column_width))

    write(divider)
    write(_print_row(header))
    write(divider)

    formatted_left_column = (' %s ' % n.ljust(left_column_width) for n in left_column)
    formatted_right_column = (' %s ' % t.ljust(right_column_width) for t in right_column)

    for formatted_row in zip(formatted_left_column, formatted_right_column):
        write(_print_row(formatted_row))

    write(divider)
