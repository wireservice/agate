from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestOrderBy(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, '👍')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

    def test_order_by(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.order_by('two')

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            self.rows[2],
            self.rows[1],
            self.rows[0]
        ])

        # Verify old table not changed
        self.assertRows(table, self.rows)

    def test_order_by_multiple_columns(self):
        rows = (
            (1, 2, 'a'),
            (2, 1, 'b'),
            (1, 1, 'c')
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.order_by(['one', 'two'])

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[2],
            rows[0],
            rows[1]
        ])

    def test_order_by_func(self):
        rows = (
            (1, 2, 'a'),
            (2, 1, 'b'),
            (1, 1, 'c')
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.order_by(lambda r: (r['one'], r['two']))

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[2],
            rows[0],
            rows[1]
        ])

    def test_order_by_reverse(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.order_by(lambda r: r['two'], reverse=True)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            self.rows[0],
            self.rows[1],
            self.rows[2]
        ])

    def test_order_by_nulls(self):
        rows = (
            (1, 2, None),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, 'a')
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.order_by('two')

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[2],
            rows[0],
            rows[1],
            rows[3]
        ])

        new_table = table.order_by('three')

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[3],
            rows[2],
            rows[0],
            rows[1]
        ])

        new_table = table.order_by(('two', 'three'))

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[2],
            rows[0],
            rows[1],
            rows[3]
        ])

    def test_order_by_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.order_by('two')

        self.assertRowNames(new_table, ['👍', 'b', 'a'])

    def test_order_by_empty_table(self):
        table = Table([], self.column_names)
        table.order_by('three')
