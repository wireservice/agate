from agate import Table
from agate.computations import Formula
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestCompute(AgateTestCase):
    def setUp(self):
        self.rows = (
            ('a', 2, 3, 4),
            (None, 3, 5, None),
            ('a', 2, 4, None),
            ('b', 3, 6, None)
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = [
            'one', 'two', 'three', 'four'
        ]
        self.column_types = [
            self.text_type, self.number_type, self.number_type, self.number_type
        ]

        self.table = Table(self.rows, self.column_names, self.column_types)

    def test_compute(self):
        new_table = self.table.compute([
            ('test', Formula(self.number_type, lambda r: r['two'] + r['three']))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'test'])
        self.assertColumnTypes(new_table, [Text, Number, Number, Number, Number])

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 5))
        self.assertSequenceEqual(new_table.columns['test'], (5, 8, 6, 9))

    def test_compute_multiple(self):
        new_table = self.table.compute([
            ('number', Formula(self.number_type, lambda r: r['two'] + r['three'])),
            ('text', Formula(self.text_type, lambda r: (r['one'] or '-') + str(r['three'])))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'number', 'text'])
        self.assertColumnTypes(new_table, [Text, Number, Number, Number, Number, Text])

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 5, 'a3'))
        self.assertSequenceEqual(new_table.columns['number'], (5, 8, 6, 9))
        self.assertSequenceEqual(new_table.columns['text'], ('a3', '-5', 'a4', 'b6'))

    def test_compute_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')

        new_table = table.compute([
            ('number', Formula(self.number_type, lambda r: r['two'] + r['three'])),
            ('text', Formula(self.text_type, lambda r: (r['one'] or '-') + str(r['three'])))
        ])

        self.assertRowNames(new_table, [3, 5, 4, 6])

    def test_compute_replace(self):
        new_table = self.table.compute([
            ('two', Formula(self.number_type, lambda r: r['two'] + r['three']))
        ], replace=True)

        self.assertIsNot(new_table, self.table)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four'])
        self.assertColumnTypes(new_table, [Text, Number, Number, Number])

        self.assertSequenceEqual(new_table.rows[0], ('a', 5, 3, 4))
        self.assertSequenceEqual(new_table.columns['two'], (5, 8, 6, 9))

    def test_compute_replace_change_type(self):
        new_table = self.table.compute([
            ('two', Formula(self.text_type, lambda r: 'a'))
        ], replace=True)

        self.assertIsNot(new_table, self.table)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four'])
        self.assertColumnTypes(new_table, [Text, Text, Number, Number])

        self.assertSequenceEqual(new_table.rows[0], ('a', 'a', 3, 4))
        self.assertSequenceEqual(new_table.columns['two'], ('a', 'a', 'a', 'a'))

    def test_compute_replace_partial(self):
        new_table = self.table.compute([
            ('two', Formula(self.number_type, lambda r: r['two'] + r['three'])),
            ('test', Formula(self.number_type, lambda r: 1))
        ], replace=True)

        self.assertIsNot(new_table, self.table)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'test'])
        self.assertColumnTypes(new_table, [Text, Number, Number, Number, Number])

        self.assertSequenceEqual(new_table.rows[0], ('a', 5, 3, 4, 1))
        self.assertSequenceEqual(new_table.columns['two'], (5, 8, 6, 9))
