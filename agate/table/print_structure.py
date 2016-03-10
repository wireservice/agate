#!/usr/bin/env python

from agate import utils


def print_structure(left_column, right_column, column_headers, output):
    """
    See :meth:`.Table.print_structure` and :meth:`.TableSet.print_structure`.
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
        line = utils.VERTICAL_LINE.join(formatted_row)

        return '%s %s %s' % (utils.VERTICAL_LINE, line, utils.VERTICAL_LINE)

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
