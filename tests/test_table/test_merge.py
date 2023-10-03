from agate import Table
from agate.data_types import Number, Text
from agate.exceptions import DataTypeError
from agate.testcase import AgateTestCase


class TestMerge(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

    def test_merge(self):
        table_a = Table(self.rows, self.column_names, self.column_types)
        table_b = Table(self.rows, self.column_names)
        table_c = Table.merge([table_a, table_b])

        self.assertIsNot(table_c, table_a)
        self.assertIsNot(table_c, table_b)
        self.assertColumnNames(table_c, self.column_names)
        self.assertColumnTypes(table_c, [Number, Number, Text])
        self.assertRows(table_c, self.rows + self.rows)

    def test_merge_different_names(self):
        table_a = Table(self.rows, self.column_names, self.column_types)

        column_names = ['a', 'b', 'c']

        table_b = Table(self.rows, column_names, self.column_types)
        table_c = Table.merge([table_a, table_b])

        self.assertIsNot(table_c, table_a)
        self.assertIsNot(table_c, table_b)
        self.assertColumnNames(table_c, self.column_names + column_names)
        self.assertColumnTypes(table_c, [Number, Number, Text, Number, Number, Text])
        self.assertSequenceEqual(table_c.rows[0], [1, 4, 'a', None, None, None])
        self.assertSequenceEqual(table_c.rows[3], [None, None, None, 1, 4, 'a'])

        for row in table_c.rows:
            self.assertSequenceEqual(row.keys(), self.column_names + column_names)

    def test_merge_mixed_names(self):
        table_a = Table(self.rows, self.column_names, self.column_types)

        column_names = ['two', 'one', 'four']

        table_b = Table(self.rows, column_names, self.column_types)
        table_c = Table.merge([table_a, table_b])

        self.assertIsNot(table_c, table_a)
        self.assertIsNot(table_c, table_b)
        self.assertColumnNames(table_c, ['one', 'two', 'three', 'four'])
        self.assertColumnTypes(table_c, [Number, Number, Text, Text])
        self.assertSequenceEqual(table_c.rows[0], [1, 4, 'a', None])
        self.assertSequenceEqual(table_c.rows[3], [4, 1, None, 'a'])

        for row in table_c.rows:
            self.assertSequenceEqual(row.keys(), ['one', 'two', 'three', 'four'])

    def test_merge_different_types(self):
        table_a = Table(self.rows, self.column_names, self.column_types)

        column_types = [self.number_type, self.text_type, self.text_type]

        table_b = Table(self.rows, self.column_names, column_types)

        with self.assertRaises(DataTypeError):
            Table.merge([table_a, table_b])

    def test_merge_with_row_names(self):
        table_a = Table(self.rows, self.column_names, self.column_types, row_names='three')

        b_rows = (
            (1, 4, 'd'),
            (2, 3, 'e'),
            (None, 2, 'f')
        )

        table_b = Table(b_rows, self.column_names, self.column_types, row_names='three')
        table_c = Table.merge([table_a, table_b], row_names='three')

        self.assertRowNames(table_c, ['a', 'b', 'c', 'd', 'e', 'f'])

    def test_merge_with_column_names(self):
        table_a = Table(self.rows, self.column_names, self.column_types, row_names='three')

        b_rows = (
            (1, 4, 'd'),
            (2, 3, 'e'),
            (None, 2, 'f')
        )

        c_rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c'),
            (None, 4, 'd'),
            (None, 3, 'e'),
            (None, 2, 'f')
        )

        table_b = Table(b_rows, ['a', 'two', 'three'], self.column_types, row_names='three')
        table_c = Table.merge([table_a, table_b], column_names=table_a.column_names)

        self.assertRows(table_c, c_rows)
