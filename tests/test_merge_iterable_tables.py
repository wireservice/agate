from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestMergeIterableTables(AgateTestCase):
    def test_generator_retains_rows_and_row_names(self):
        tables = [
            Table([('a', 2)], ['name', 'value'], [Text(), Number()]),
            Table([('b', 3)], ['name', 'value'], [Text(), Number()])
        ]

        result = Table.merge((table for table in tables), row_names='name')

        self.assertRows(result, [('a', 2), ('b', 3)])
        self.assertRowNames(result, ['a', 'b'])
        self.assertRows(tables[0], [('a', 2)])

    def test_iterator_merges_different_column_orders(self):
        first = Table([('a', 2)], ['name', 'value'], [Text(), Number()])
        second = Table([(3, 'b', 'extra')], ['value', 'name', 'note'], [Number(), Text(), Text()])

        result = Table.merge(iter([first, second]))

        self.assertColumnNames(result, ['name', 'value', 'note'])
        self.assertRows(result, [('a', 2, None), ('b', 3, 'extra')])

    def test_generator_with_selected_columns(self):
        table = Table([('a', 2)], ['name', 'value'], [Text(), Number()])

        result = Table.merge(iter([table]), column_names=['value'])

        self.assertColumnNames(result, ['value'])
        self.assertRows(result, [(2,)])

    def test_empty_iterator(self):
        result = Table.merge(iter([]))

        self.assertColumnNames(result, [])
        self.assertRows(result, [])
