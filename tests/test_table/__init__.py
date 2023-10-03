import warnings
from decimal import Decimal

from agate import Table
from agate.computations import Formula
from agate.data_types import Number, Text
from agate.exceptions import CastError
from agate.testcase import AgateTestCase
from agate.warns import DuplicateColumnWarning


class TestBasic(AgateTestCase):
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

    def test_create_table(self):
        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table, ['a', 'b', 'c'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_filename(self):
        with self.assertRaises(ValueError):
            Table('foo.csv')

    def test_create_empty_table(self):
        table = Table([])
        table2 = Table([], self.column_names, self.column_types)

        self.assertColumnNames(table, [])
        self.assertColumnTypes(table, [])
        self.assertRows(table, [])

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Number, Text])
        self.assertRows(table2, [])

    def test_create_table_column_types(self):
        column_types = [self.number_type, self.text_type, self.text_type]

        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows, column_types=column_types)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table, ['a', 'b', 'c'])
        self.assertColumnTypes(table, [Number, Text, Text])
        self.assertRows(table, [
            (1, '4', 'a'),
            (2, '3', 'b'),
            (None, '2', '👍')
        ])

    def test_create_table_column_types_dict(self):
        column_types = dict(zip(self.column_names, self.column_types))
        table = Table(self.rows, column_names=self.column_names, column_types=column_types)

        self.assertColumnNames(table, ['one', 'two', 'three'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_table_partial_column_types_dict(self):
        column_types = dict(zip(self.column_names[:2], self.column_types[:2]))
        table = Table(self.rows, column_names=self.column_names, column_types=column_types)

        self.assertColumnNames(table, ['one', 'two', 'three'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_table_column_names(self):
        table = Table(self.rows, self.column_names)

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_table_column_types_and_names(self):
        table = Table(self.rows, self.column_names, self.column_types)

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_table_non_string_columns(self):
        column_names = ['one', 'two', 3]

        with self.assertRaises(ValueError):
            Table(self.rows, column_names, self.column_types)

    def test_create_table_cast_error(self):
        column_types = [self.number_type, self.number_type, self.number_type]

        with self.assertRaises(CastError) as e:
            Table(self.rows, self.column_names, column_types)

        self.assertIn('Error at row 0 column three.', str(e.exception))

    def test_create_table_null_column_names(self):
        column_names = ['one', None, 'three']

        with self.assertWarns(RuntimeWarning):
            Table(self.rows, column_names, self.column_types)

        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows, column_names, self.column_types)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table, ['one', 'b', 'three'])

    def test_create_table_empty_column_names(self):
        column_names = ['one', '', 'three']

        with self.assertWarns(RuntimeWarning):
            Table(self.rows, column_names, self.column_types)

        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows, column_names, self.column_types)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table, ['one', 'b', 'three'])

    def test_create_table_non_datatype_columns(self):
        column_types = [self.number_type, self.number_type, 'foo']

        with self.assertRaises(ValueError):
            Table(self.rows, self.column_names, column_types)

    def test_create_duplicate_column_names(self):
        column_names = ['one', 'two', 'two']

        with self.assertWarns(DuplicateColumnWarning):
            table = Table(self.rows, column_names, self.column_types)

        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows, column_names, self.column_types)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table, ['one', 'two', 'two_2'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_column_names_types_different_lengths(self):
        column_names = ['one', 'two', 'three', 'four']

        with self.assertRaises(ValueError):
            Table(self.rows, column_names, self.column_types)

    def test_create_variable_length_rows(self):
        rows = (
            (1, 4, 'a'),
            (2,),
            (None, 2)
        )

        table = Table(rows, self.column_names, self.column_types)

        warnings.simplefilter('ignore')

        try:
            table2 = Table(rows)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, [
            (1, 4, 'a'),
            (2, None, None),
            (None, 2, None)
        ])

        self.assertColumnTypes(table2, [Number, Number, Text])
        self.assertRows(table2, [
            (1, 4, 'a'),
            (2, None, None),
            (None, 2, None)
        ])

    def test_create_table_no_column_names(self):
        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows, None, self.column_types)
        finally:
            warnings.resetwarnings()

        self.assertEqual(len(table.rows), 3)
        self.assertEqual(len(table.columns), 3)

        self.assertSequenceEqual(table.columns[0], (1, 2, None))
        self.assertSequenceEqual(table.columns['a'], (1, 2, None))

        with self.assertRaises(KeyError):
            table.columns[None]

        with self.assertRaises(KeyError):
            table.columns['one']

        self.assertSequenceEqual(table.columns[2], ('a', 'b', '👍'))
        self.assertSequenceEqual(table.columns['c'], ('a', 'b', '👍'))

        with self.assertRaises(KeyError):
            table.columns['']

    def test_no_column_name_warning(self):
        with self.assertWarnsRegex(RuntimeWarning, 'Column 1 has no name. Using "b".'):
            Table(self.rows, ['a', None, 'c'], self.column_types)

        with self.assertWarnsRegex(RuntimeWarning, 'Column 1 has no name. Using "b".'):
            Table(self.rows, ['a', '', 'c'], self.column_types)

    def test_row_too_long(self):
        rows = (
            (1, 4, 'a', 'foo'),
            (2,),
            (None, 2)
        )

        with self.assertRaises(ValueError):
            Table(rows, self.column_names, self.column_types)

    def test_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')

        self.assertRowNames(table, ['a', 'b', '👍'])

    def test_row_names_non_string(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names=[Decimal('2'), True, None])

        self.assertSequenceEqual(table.row_names, [
            Decimal('2'),
            True,
            None,
        ])
        self.assertSequenceEqual(table.rows[Decimal('2')], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[True], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[None], (None, 2, '👍'))

    def test_row_names_int(self):
        with self.assertRaises(ValueError):
            Table(self.rows, self.column_names, self.column_types, row_names=['a', 'b', 3])

    def test_row_names_func(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names=lambda r: (r['one'], r['three']))

        self.assertSequenceEqual(table.row_names, [
            (Decimal('1'), 'a'),
            (Decimal('2'), 'b'),
            (None, '👍')
        ])
        self.assertSequenceEqual(table.rows[(Decimal('1'), 'a')], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[(Decimal('2'), 'b')], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[(None, '👍')], (None, 2, '👍'))

    def test_row_names_invalid(self):

        with self.assertRaises(ValueError):
            Table(
                self.rows,
                self.column_names,
                self.column_types,
                row_names={'a': 1, 'b': 2, 'c': 3}
            )

    def test_stringify(self):
        column_names = ['foo', 'bar', '👍']

        table = Table(self.rows, column_names)

        u = str(table)

        self.assertIn('foo', u)
        self.assertIn('bar', u)
        self.assertIn('👍', u)

    def test_str(self):
        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table, ['a', 'b', 'c'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_iter(self):
        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows)
        finally:
            warnings.resetwarnings()

        for row, table_row, row_row in zip(self.rows, table, table.rows):
            self.assertEqual(row, table_row, row_row)

    def test_indexing(self):
        warnings.simplefilter('ignore')

        try:
            table = Table(self.rows)
        finally:
            warnings.resetwarnings()

        self.assertEqual(table[1], self.rows[1])
        self.assertEqual(table[-1], self.rows[-1])
        self.assertEqual(table[1:2], self.rows[1:2])

    def test_get_column_types(self):
        table = Table(self.rows, self.column_names, self.column_types)

        self.assertSequenceEqual(table.column_types, self.column_types)

    def test_get_column_names(self):
        table = Table(self.rows, self.column_names, self.column_types)

        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_select(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.select(('two', 'three'))

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, ['two', 'three'])
        self.assertColumnTypes(new_table, [Number, Text])
        self.assertRows(new_table, [
            [4, 'a'],
            [3, 'b'],
            [2, '👍']
        ])

    def test_select_single(self):
        table = Table(self.rows, self.column_names, self.column_types)
        new_table = table.select('three')

        self.assertColumnNames(new_table, ['three'])
        self.assertColumnTypes(new_table, [Text])
        self.assertRows(new_table, [
            ['a'],
            ['b'],
            ['👍']
        ])

    def test_select_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.select(('three',))

        self.assertRowNames(new_table, ['a', 'b', '👍'])

    def test_select_does_not_exist(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with self.assertRaises(ValueError):
            table.select(('four',))

    def test_exclude(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.exclude(('one', 'two'))

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, ['three'])
        self.assertColumnTypes(new_table, [Text])
        self.assertRows(new_table, [
            ['a'],
            ['b'],
            ['👍']
        ])

    def test_exclude_single(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.exclude('one')

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, ['two', 'three'])
        self.assertColumnTypes(new_table, [Number, Text])
        self.assertRows(new_table, [
            [4, 'a'],
            [3, 'b'],
            [2, '👍']
        ])

    def test_exclude_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.exclude(('one', 'two'))

        self.assertRowNames(new_table, ['a', 'b', '👍'])

    def test_where(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.where(lambda r: r['one'] in (2, None))

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            self.rows[1],
            self.rows[2]
        ])

    def test_where_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.where(lambda r: r['one'] in (2, None))

        self.assertRowNames(new_table, ['b', '👍'])

    def test_find(self):
        table = Table(self.rows, self.column_names, self.column_types)

        row = table.find(lambda r: r['two'] - r['one'] == 1)

        self.assertIs(row, table.rows[1])

    def test_find_none(self):
        table = Table(self.rows, self.column_names, self.column_types)

        row = table.find(lambda r: r['one'] == 'FOO')

        self.assertIs(row, None)

    def test_limit(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(2)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, self.rows[:2])

    def test_limit_slice(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(0, 3, 2)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, self.rows[0:3:2])

    def test_limit_slice_negative(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(-2, step=-1)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, self.rows[-2:-1])

    def test_limit_step_only(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(step=2)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, self.rows[::2])

    def test_limit_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.limit(2)

        self.assertRowNames(new_table, ['a', 'b'])

    def test_distinct_column(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.distinct('one')

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[0],
            rows[1]
        ])

    def test_distinct_multiple_columns(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.distinct(['two', 'three'])

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[0],
            rows[1],
            rows[2]
        ])

    def test_distinct_func(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.distinct(lambda row: (row['two'], row['three']))

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[0],
            rows[1],
            rows[2]
        ])

    def test_distinct_none(self):
        rows = (
            (1, 2, 'a'),
            (1, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.distinct()

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[0],
            rows[1],
            rows[2]
        ])

    def test_distinct_with_row_names(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, 'd')
        )

        table = Table(rows, self.column_names, self.column_types, row_names='three')
        new_table = table.distinct('one')

        self.assertRowNames(new_table, ['a', None])

    def test_chain_select_where(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.select(('one', 'two')).where(lambda r: r['two'] == 3)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names[:2])
        self.assertColumnTypes(new_table, [Number, Number])
        self.assertRows(new_table, [
            self.rows[1][:2],
        ])


class TestData(AgateTestCase):
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

    def test_data_immutable(self):
        rows = [
            [1, 4, 'a'],
            [2, 3, 'b'],
            [None, 2, 'c']
        ]

        table = Table(rows, self.column_names, self.column_types)
        rows[0] = [2, 2, 2]
        self.assertSequenceEqual(table.rows[0], [1, 4, 'a'])

    def test_fork_preserves_data(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table._fork(table.rows)

        self.assertIs(table.rows[0], table2.rows[0])
        self.assertIs(table.rows[1], table2.rows[1])
        self.assertIs(table.rows[2], table2.rows[2])

    def test_where_preserves_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.where(lambda r: r['one'] == 1)
        table3 = table2.where(lambda r: r['one'] == 1)

        self.assertIs(table.rows[0], table2.rows[0])
        self.assertIs(table2.rows[0], table3.rows[0])

    def test_order_by_preserves_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.order_by(lambda r: r['one'])
        table3 = table2.order_by(lambda r: r['one'])

        self.assertIs(table.rows[0], table2.rows[0])
        self.assertIs(table2.rows[0], table3.rows[0])

    def test_limit_preserves_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.limit(2)
        table3 = table2.limit(2)

        self.assertIs(table.rows[0], table2.rows[0])
        self.assertIs(table2.rows[0], table3.rows[0])

    def test_compute_creates_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.compute([
            ('new2', Formula(self.number_type, lambda r: r['one']))
        ])
        table3 = table2.compute([
            ('new3', Formula(self.number_type, lambda r: r['one']))
        ])

        self.assertIsNot(table.rows[0], table2.rows[0])
        self.assertNotEqual(table.rows[0], table2.rows[0])
        self.assertIsNot(table2.rows[0], table3.rows[0])
        self.assertNotEqual(table2.rows[0], table3.rows[0])
        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))
