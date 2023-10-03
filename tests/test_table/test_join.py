from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestJoin(AgateTestCase):
    def setUp(self):
        self.left_rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )

        self.right_rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.left_column_names = ['one', 'two', 'three']
        self.right_column_names = ['four', 'five', 'six']
        self.column_types = [self.number_type, self.number_type, self.text_type]

        self.left = Table(self.left_rows, self.left_column_names, self.column_types)
        self.right = Table(self.right_rows, self.right_column_names, self.column_types)

    def test_join(self):
        new_table = self.left.join(self.right, 'one', 'four')

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 4, 'a'),
            (2, 3, 'b', 3, 'b'),
            (None, 2, 'c', 2, 'c')
        ])

    def test_join_column_indicies(self):
        new_table = self.left.join(self.right, 0, 0)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 4, 'a'),
            (2, 3, 'b', 3, 'b'),
            (None, 2, 'c', 2, 'c')
        ])

    def test_join_match_multiple(self):
        left_rows = (
            (1, 4, 'a'),
            (2, 3, 'b')
        )

        right_rows = (
            (1, 1, 'a'),
            (1, 2, 'a'),
            (2, 2, 'b')
        )

        left = Table(left_rows, self.left_column_names, self.column_types)
        right = Table(right_rows, self.right_column_names, self.column_types)
        new_table = left.join(right, 'one', 'five')

        self.assertIsNot(new_table, left)
        self.assertIsNot(new_table, right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 'a'),
            (2, 3, 'b', 1, 'a'),
            (2, 3, 'b', 2, 'b')
        ])

    def test_join2(self):
        new_table = self.left.join(self.right, 'one', 'five')

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', None, None),
            (2, 3, 'b', None, 'c'),
            (None, 2, 'c', None, None)
        ])

    def test_join_same_column_name(self):
        right_column_names = ['four', 'one', 'six']

        right = Table(self.right_rows, right_column_names, self.column_types)

        new_table = self.left.join(right, 'one')

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', None, None),
            (2, 3, 'b', None, 'c'),
            (None, 2, 'c', None, None)
        ])

    def test_join_multiple_columns(self):
        new_table = self.left.join(
            self.right,
            ['two', 'three'],
            ['five', 'six']
        )

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number])
        self.assertRows(new_table, [
            (1, 4, 'a', 1),
            (2, 3, 'b', 2),
            (None, 2, 'c', None)
        ])

    def test_join_func(self):
        new_table = self.left.join(
            self.right,
            lambda left: '%i%s' % (left['two'], left['three']),
            lambda right: '%i%s' % (right['five'], right['six'])
        )

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 4, 'a'),
            (2, 3, 'b', 2, 3, 'b'),
            (None, 2, 'c', None, 2, 'c')
        ])

    def test_join_column_does_not_exist(self):
        with self.assertRaises(KeyError):
            self.left.join(self.right, 'one', 'seven')

    def test_inner_join(self):
        new_table = self.left.join(self.right, 'one', 'four', inner=True)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 4, 'a'),
            (2, 3, 'b', 3, 'b'),
            (None, 2, 'c', 2, 'c')
        ])

    def test_inner_join2(self):
        new_table = self.left.join(self.right, 'one', 'five', inner=True)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (2, 3, 'b', None, 'c')
        ])

    def test_inner_join_same_column_name(self):
        right_column_names = ['four', 'one', 'six']

        right = Table(self.right_rows, right_column_names, self.column_types)

        new_table = self.left.join(right, 'one', inner=True)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (2, 3, 'b', None, 'c')
        ])

    def test_inner_join_func(self):
        new_table = self.left.join(
            self.right,
            lambda left: '%i%s' % (left['two'], left['three']),
            lambda right: '%i%s' % (right['five'], right['six']),
            inner=True
        )

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 4, 'a')
        ])

    def test_join_with_row_names(self):
        left = Table(self.left_rows, self.left_column_names, self.column_types, row_names='three')
        new_table = left.join(self.right, 'one', 'four')

        self.assertRowNames(new_table, ('a', 'b', 'c'))

    def test_join_require_match(self):
        with self.assertRaises(ValueError):
            self.left.join(self.right, 'one', 'five', require_match=True)

        with self.assertRaises(ValueError):
            self.left.join(self.right, 'one', 'five', require_match=True)

        self.left.join(self.right, 'one', 'four', require_match=True)

    def test_join_columns_kwarg(self):
        new_table = self.left.join(self.right, 'one', 'four', columns=['six'])

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 'a'),
            (2, 3, 'b', 'b'),
            (None, 2, 'c', 'c')
        ])

    def test_join_columns_kwarg_right_key(self):
        new_table = self.left.join(self.right, 'one', 'four', columns=['four', 'six'])

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 'a'),
            (2, 3, 'b', 2, 'b'),
            (None, 2, 'c', None, 'c')
        ])

    def test_join_rows_are_tuples(self):
        new_table = self.left.join(self.right, 'one', 'four', columns=['four', 'six'])

        self.assertIsInstance(new_table.rows[0].values(), tuple)

    def test_full_outer(self):
        left_rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (3, 2, 'c')
        )

        right_rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (4, 2, 'c')
        )

        left = Table(left_rows, self.left_column_names, self.column_types)
        right = Table(right_rows, self.right_column_names, self.column_types)

        new_table = left.join(right, 'one', 'four', full_outer=True)

        self.assertIsNot(new_table, left)
        self.assertIsNot(new_table, right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 4, 'a'),
            (2, 3, 'b', 2, 3, 'b'),
            (3, 2, 'c', None, None, None),
            (None, None, None, 4, 2, 'c')
        ])

    def test_join_by_row_number(self):
        new_table = self.left.join(self.right, full_outer=True)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 4, 'a'),
            (2, 3, 'b', 2, 3, 'b'),
            (None, 2, 'c', None, 2, 'c')
        ])

    def test_join_by_row_number_short_right(self):
        right_rows = self.right_rows + ((7, 9, 'z'),)
        right = Table(right_rows, self.right_column_names, self.column_types)

        new_table = self.left.join(right, full_outer=True)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 4, 'a'),
            (2, 3, 'b', 2, 3, 'b'),
            (None, 2, 'c', None, 2, 'c'),
            (None, None, None, 7, 9, 'z')
        ])

    def test_join_by_row_number_short_left(self):
        left_rows = self.left_rows + ((7, 9, 'z'),)
        left = Table(left_rows, self.left_column_names, self.column_types)

        new_table = left.join(self.right, full_outer=True)

        self.assertIsNot(new_table, left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 4, 'a'),
            (2, 3, 'b', 2, 3, 'b'),
            (None, 2, 'c', None, 2, 'c'),
            (7, 9, 'z', None, None, None)
        ])
