import warnings

from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestRename(AgateTestCase):
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

    def test_rename_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(row_names=['a', 'b', 'c'])

        self.assertSequenceEqual(table2.row_names, ['a', 'b', 'c'])
        self.assertSequenceEqual(table2.column_names, self.column_names)

        self.assertIs(table.row_names, None)
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_row_names_dict(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names=['a', 'b', 'c'])
        table2 = table.rename(row_names={'b': 'd'})

        self.assertSequenceEqual(table2.row_names, ['a', 'd', 'c'])
        self.assertSequenceEqual(table2.column_names, self.column_names)

        self.assertSequenceEqual(table.row_names, ['a', 'b', 'c'])
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_column_names(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(column_names=['d', 'e', 'f'])

        self.assertIs(table2.row_names, None)
        self.assertSequenceEqual(table2.column_names, ['d', 'e', 'f'])

        self.assertIs(table.row_names, None)
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_column_names_dict(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(column_names={'two': 'second'})

        self.assertIs(table2.row_names, None)
        self.assertSequenceEqual(table2.column_names, ['one', 'second', 'three'])

        self.assertIs(table.row_names, None)
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_column_names_renames_row_values(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_column_names = ['d', 'e', 'f']
        table2 = table.rename(column_names=new_column_names)

        self.assertColumnNames(table2, new_column_names)

    def test_rename_slugify_columns(self):
        strings = ['Test kož', 'test 2', 'test 2']

        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(strings, slug_columns=True)
        table3 = table.rename(strings, slug_columns=True, separator='.')

        self.assertColumnNames(table, ['one', 'two', 'three'])
        self.assertColumnNames(table2, ['test_koz', 'test_2', 'test_2_2'])
        self.assertColumnNames(table3, ['test.koz', 'test.2', 'test.2.2'])

    def test_rename_slugify_rows(self):
        strings = ['Test kož', 'test 2', 'test 2']

        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(row_names=strings, slug_rows=True)
        table3 = table.rename(row_names=strings, slug_rows=True, separator='.')

        self.assertIs(table.row_names, None)
        self.assertRowNames(table2, ['test_koz', 'test_2', 'test_2_2'])
        self.assertRowNames(table3, ['test.koz', 'test.2', 'test.2.2'])

    def test_rename_slugify_columns_in_place(self):
        column_names = ['Test kož', 'test 2', 'test 2']

        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows, column_names, self.column_types)
        finally:
            warnings.resetwarnings()

        table2 = table.rename(slug_columns=True)
        table3 = table.rename(slug_columns=True, separator='.')

        self.assertColumnNames(table, ['Test kož', 'test 2', 'test 2_2'])
        self.assertColumnNames(table2, ['test_koz', 'test_2', 'test_2_2'])
        self.assertColumnNames(table3, ['test.koz', 'test.2', 'test.2.2'])

    def test_rename_slugify_rows_in_place(self):
        strings = ['Test kož', 'test 2', 'test 2']

        table = Table(self.rows, self.column_names, self.column_types, row_names=strings)
        table2 = table.rename(slug_rows=True)
        table3 = table.rename(slug_rows=True, separator='.')

        self.assertRowNames(table, ['Test kož', 'test 2', 'test 2'])
        self.assertRowNames(table2, ['test_koz', 'test_2', 'test_2_2'])
        self.assertRowNames(table3, ['test.koz', 'test.2', 'test.2.2'])
