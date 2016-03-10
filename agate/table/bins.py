#!/usr/bin/env python

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

from babel.numbers import format_decimal

from agate.aggregations import Min, Max
from agate import utils


def bins(self, column_name, count, start, end):
    """
    See :meth:`.Table.bins`.
    """
    # Infer bin start/end positions
    if start is None or end is None:
        start, end = utils.round_limits(
            Min(column_name).run(self),
            Max(column_name).run(self)
        )
    else:
        start = Decimal(start)
        end = Decimal(end)

    # Calculate bin size
    spread = abs(end - start)
    size = spread / count

    breaks = [start]

    # Calculate breakpoints
    for i in range(1, count + 1):
        top = start + (size * i)

        breaks.append(top)

    # Format bin names
    decimal_places = utils.max_precision(breaks)
    break_formatter = utils.make_number_formatter(decimal_places)

    def name_bin(i, j, first_exclusive=True, last_exclusive=False):
        inclusive = format_decimal(i, format=break_formatter)
        exclusive = format_decimal(j, format=break_formatter)

        output = u'[' if first_exclusive else u'('
        output += u'%s - %s' % (inclusive, exclusive)
        output += u']' if last_exclusive else u')'

        return output

    # Generate bins
    bin_names = []

    for i in range(1, len(breaks)):
        last_exclusive = (i == len(breaks) - 1)
        name = name_bin(breaks[i - 1], breaks[i], last_exclusive=last_exclusive)

        bin_names.append(name)

    bin_names.append(None)

    # Lambda method for actually assigning values to bins
    def binner(row):
        value = row[column_name]

        if value is None:
            return None

        i = 1

        try:
            while value >= breaks[i]:
                i += 1
        except IndexError:
            i -= 1

        return bin_names[i - 1]

    # Pivot by lambda
    table = self.pivot(binner, key_name=column_name)

    # Sort by bin order
    return table.order_by(lambda r: bin_names.index(r[column_name]))
