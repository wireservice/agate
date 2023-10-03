from decimal import Decimal

from babel.numbers import get_decimal_symbol

from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestBins(AgateTestCase):
    def setUp(self):
        self.number_type = Number()
        self.column_names = ['number']
        self.column_types = [self.number_type]

    def test_bins(self):
        rows = []

        for i in range(0, 100):
            rows.append([i]),

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertColumnNames(new_table, ['number', 'Count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(new_table.rows[0], ['[0 - 10)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[30 - 40)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[90 - 100]', 10])

        self.assertRowNames(new_table, [
            '[0 - 10)',
            '[10 - 20)',
            '[20 - 30)',
            '[30 - 40)',
            '[40 - 50)',
            '[50 - 60)',
            '[60 - 70)',
            '[70 - 80)',
            '[80 - 90)',
            '[90 - 100]',
        ])

    def test_bins_negative(self):
        rows = []

        for i in range(0, -100, -1):
            rows.append([i])

        new_table = Table(rows, self.column_names, self.column_types).bins('number', 10, start=-100)

        self.assertColumnNames(new_table, ['number', 'Count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(new_table.rows[0], ['[-100 - -90)', 9])
        self.assertSequenceEqual(new_table.rows[3], ['[-70 - -60)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[-10 - 0]', 11])

    def test_bins_mixed_signs(self):
        rows = []

        for i in range(0, -100, -1):
            rows.append([i + 50])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertColumnNames(new_table, ['number', 'Count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(new_table.rows[0], ['[-50 - -40)', 9])
        self.assertSequenceEqual(new_table.rows[3], ['[-20 - -10)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[40 - 50]', 11])

    def test_bins_small_numbers(self):
        rows = []

        for i in range(0, 100):
            rows.append([Decimal(i) / Decimal('10')])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertSequenceEqual(new_table.rows[0], ['[0 - 1)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[3 - 4)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[9 - 10]', 10])

    def test_bins_values_outside_start_end(self):
        rows = []

        for i in range(0, 100):
            rows.append([Decimal(i) / Decimal('10')])

        table_one = Table(rows, self.column_names, self.column_types).bins('number', start=1, end=11)
        table_two = Table(rows, self.column_names, self.column_types).bins('number', start=-1, end=9)

        self.assertSequenceEqual(table_one.rows[0], ['[0 - 2)', 20])
        self.assertSequenceEqual(table_two.rows[8], ['[8 - 10]', 20])

    def test_bins_decimals(self):
        rows = []

        for i in range(0, 100):
            rows.append([Decimal(i) / Decimal('100')])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertColumnNames(new_table, ['number', 'Count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(
            new_table.rows[0],
            ['[0' + get_decimal_symbol() + '0 - 0' + get_decimal_symbol() + '1)', 10]
        )
        self.assertSequenceEqual(
            new_table.rows[3],
            ['[0' + get_decimal_symbol() + '3 - 0' + get_decimal_symbol() + '4)', 10]
        )
        self.assertSequenceEqual(
            new_table.rows[9],
            ['[0' + get_decimal_symbol() + '9 - 1' + get_decimal_symbol() + '0]', 10]
        )

    def test_bins_nulls(self):
        rows = []

        for i in range(0, 100):
            rows.append([Decimal(i) / Decimal('100')])

        rows.append([None])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertColumnNames(new_table, ['number', 'Count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(
            new_table.rows[0],
            ['[0' + get_decimal_symbol() + '0 - 0' + get_decimal_symbol() + '1)', 10]
        )
        self.assertSequenceEqual(
            new_table.rows[3],
            ['[0' + get_decimal_symbol() + '3 - 0' + get_decimal_symbol() + '4)', 10]
        )
        self.assertSequenceEqual(
            new_table.rows[9],
            ['[0' + get_decimal_symbol() + '9 - 1' + get_decimal_symbol() + '0]', 10]
        )
        self.assertSequenceEqual(new_table.rows[10], [None, 1])
