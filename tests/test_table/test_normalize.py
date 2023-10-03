from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase
from agate.type_tester import TypeTester


class TestNormalize(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 'c', 4, 'a'),
            (2, 'e', 3, 'b'),
            (None, 'g', 2, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three', 'four']
        self.column_types = [self.number_type, self.text_type, self.number_type, self.text_type]

    def test_normalize(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('one', 'three')

        normal_rows = (
            (1, 'three', 4),
            (2, 'three', 3),
            (None, 'three', 2)
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Number])

    def test_normalize_column_types(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('one', 'three', column_types=[Text(), Text()])

        normal_rows = (
            (1, 'three', '4'),
            (2, 'three', '3'),
            (None, 'three', '2')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text])

    def test_normalize_column_type_tester(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('one', 'three', column_types=TypeTester(force={'value': Text()}))

        normal_rows = (
            (1, 'three', '4'),
            (2, 'three', '3'),
            (None, 'three', '2')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text])

    def test_normalize_multiple_fields(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('one', ['three', 'four'])

        normal_rows = (
            (1, 'three', '4'),
            (1, 'four', 'a'),
            (2, 'three', '3'),
            (2, 'four', 'b'),
            (None, 'three', '2'),
            (None, 'four', 'c')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text])

    def test_normalize_multiple_keys(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize(['one', 'two'], ['three', 'four'])

        normal_rows = (
            (1, 'c', 'three', '4'),
            (1, 'c', 'four', 'a'),
            (2, 'e', 'three', '3'),
            (2, 'e', 'four', 'b'),
            (None, 'g', 'three', '2'),
            (None, 'g', 'four', 'c')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['one', 'two', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text, Text])

    def test_normalize_change_order(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.normalize('three', ['one', 'four'])

        normal_rows = (
            (4, 'one', '1'),
            (4, 'four', 'a'),
            (3, 'one', '2'),
            (3, 'four', 'b'),
            (2, 'one', None),
            (2, 'four', 'c')
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['three', 'property', 'value'])
        self.assertColumnTypes(normalized_table, [Number, Text, Text])
