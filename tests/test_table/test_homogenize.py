from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestHomogenize(AgateTestCase):
    def setUp(self):
        self.rows = (
            (0, 4, 'a'),
            (1, 3, 'b'),
            (None, 2, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

    def test_homogenize_column_name(self):
        table = Table(self.rows, self.column_names, self.column_types)
        compare_values = range(3)
        homogenized = table.homogenize('one', compare_values, [3, 'd'])
        rows = (
            (0, 4, 'a'),
            (1, 3, 'b'),
            (None, 2, 'c'),
            (2, 3, 'd')
        )

        homogenized.print_table()

        self.assertColumnNames(homogenized, self.column_names)
        self.assertColumnTypes(homogenized, [Number, Number, Text])
        self.assertRows(homogenized, rows)

    def test_homogenize_default_row(self):
        table = Table(self.rows, self.column_names, self.column_types)
        compare_values = [0, 1, 2]
        homogenized = table.homogenize(['one'], compare_values)
        rows = (
            (0, 4, 'a'),
            (1, 3, 'b'),
            (None, 2, 'c'),
            (2, None, None)
        )

        homogenized.print_table()

        self.assertColumnNames(homogenized, self.column_names)
        self.assertColumnTypes(homogenized, [Number, Number, Text])
        self.assertRows(homogenized, rows)

    def test_homogenize_multiple_columns(self):
        table = Table(self.rows, self.column_names, self.column_types)

        def column_two(count):
            return [chr(ord('a') + c) for c in range(count)]

        homogenized = table.homogenize(['one', 'three'], zip(range(3), column_two(3)), [5])
        rows = (
            (0, 4, 'a'),
            (1, 3, 'b'),
            (None, 2, 'c'),
            (2, 5, 'c')
        )

        homogenized.print_table()

        self.assertColumnNames(homogenized, self.column_names)
        self.assertColumnTypes(homogenized, [Number, Number, Text])
        self.assertRows(homogenized, rows)

    def test_homogenize_lambda_default(self):
        table = Table(self.rows, self.column_names, self.column_types)

        def default_row(d):
            return [d[0], d[0] * 2, d[1]]

        def column_two(count):
            return [chr(ord('a') + c) for c in range(count)]

        homogenized = table.homogenize(['one', 'three'], zip(range(3), column_two(3)), default_row)
        rows = (
            (0, 4, 'a'),
            (1, 3, 'b'),
            (None, 2, 'c'),
            (2, 4, 'c')
        )

        homogenized.print_table()

        self.assertColumnNames(homogenized, self.column_names)
        self.assertColumnTypes(homogenized, [Number, Number, Text])
        self.assertRows(homogenized, rows)
