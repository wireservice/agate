#!/usr/bin/env python

from decimal import Decimal

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import journalism

class TestTable(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )
        self.column_names = ('one', 'two', 'three')
        self.column_types = (journalism.IntColumn, journalism.IntColumn, journalism.TextColumn)

    def test_create_table(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        self.assertEqual(len(table.rows), 3)

        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[2], (None, 2, 'c'))

    def test_column_names_immutable(self):
        column_names = ['one', 'two', 'three']
        
        table = journalism.Table(self.rows, self.column_types, column_names)

        column_names[0] = 'five'

        self.assertEqual(table.get_column_names()[0], 'one')

    def test_cast_table(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names, cast=True)

        self.assertEqual(len(table.rows), 3)

        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[2], (None, 2, 'c'))

    def test_validate_table(self):
        journalism.Table(self.rows, self.column_types, self.column_names, validate=True)

    def test_validate_table_fails(self):
        column_types = [journalism.IntColumn, journalism.IntColumn, journalism.IntColumn]

        with self.assertRaises(journalism.ColumnValidationError):
            journalism.Table(self.rows, column_types, self.column_names, validate=True)

    def test_get_column_types(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        self.assertEqual(table.get_column_types(), self.column_types)

    def test_get_column_names(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        self.assertSequenceEqual(table.get_column_names(), ('one', 'two', 'three'))

    def test_select(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.select(('three',))

        self.assertIsNot(new_table, table)
        
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], ('a',))
        self.assertSequenceEqual(new_table.rows[1], ('b',))
        self.assertSequenceEqual(new_table.rows[2], ('c',))
        
        self.assertEqual(len(new_table.columns), 1)
        self.assertSequenceEqual(new_table._column_types, (journalism.TextColumn,))
        self.assertSequenceEqual(new_table._column_names, ('three',))
        self.assertSequenceEqual(new_table.columns['three'], ('a', 'b', 'c'))

    def test_where(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.where(lambda r: r['one'] in (2, None))

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.columns['one'], (2, None))

    def test_order_by(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.order_by('two')

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (None, 2, 'c'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (1, 4, 'a'))

        # Verify old table not changed
        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[2], (None, 2, 'c'))

    def test_order_by_func(self):
        rows = (
            (1, 2, 'a'),
            (2, 1, 'b'),
            (1, 1, 'c')
        )

        table = journalism.Table(rows, self.column_types, self.column_names)

        new_table = table.order_by(lambda r: (r['one'], r['two']))

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 1, 'c'))
        self.assertSequenceEqual(new_table.rows[1], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.rows[2], (2, 1, 'b'))

    def test_order_by_reverse(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.order_by(lambda r: r['two'], reverse=True)

        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c'))

    def test_order_by_nulls(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = journalism.Table(rows, self.column_types, self.column_names)

        new_table = table.order_by(lambda r: r['two'])

        self.assertSequenceEqual(new_table.columns['two'], (1, 2, None, None))

        new_table = table.order_by(lambda r: r['three'])

        self.assertSequenceEqual(new_table.columns['three'], ('a', 'c', None, None))

    def test_limit(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.limit(2)

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.columns['one'], (1, 2))

    def test_limit_slice(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.limit(0, 3, 2)

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (None, 2, 'c'))
        self.assertSequenceEqual(new_table.columns['one'], (1, None))

    def test_limit_slice_negative(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.limit(-2, step=-1)

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[1], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.columns['one'], (2, 1))

    def test_limit_step_only(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.limit(step=2)

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (None, 2, 'c'))
        self.assertSequenceEqual(new_table.columns['one'], (1, None))

    def test_distinct_column(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = journalism.Table(rows, self.column_types, self.column_names)

        new_table = table.distinct('one')

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, None, None))
        self.assertSequenceEqual(new_table.columns['one'], (1, 2))

    def test_distinct_func(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = journalism.Table(rows, self.column_types, self.column_names)

        new_table = table.distinct(lambda row: (row['two'], row['three']))

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, None, None))
        self.assertSequenceEqual(new_table.rows[2], (1, 1, 'c'))
        self.assertSequenceEqual(new_table.columns['one'], (1, 2, 1))

    def test_distinct_none(self):
        rows = (
            (1, 2, 'a'),
            (1, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = journalism.Table(rows, self.column_types, self.column_names)

        new_table = table.distinct()

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (1, None, None))
        self.assertSequenceEqual(new_table.rows[2], (1, 1, 'c'))
        self.assertSequenceEqual(new_table.columns['one'], (1, 1, 1))

    def test_chain_select_where(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.select(('one', 'two')).where(lambda r: r['two'] == 3)

        self.assertEqual(len(new_table.rows), 1)
        self.assertSequenceEqual(new_table.rows[0], (2, 3))
        
        self.assertEqual(len(new_table.columns), 2)
        self.assertSequenceEqual(new_table._column_types, (journalism.IntColumn, journalism.IntColumn))
        self.assertEqual(new_table._column_names, ('one', 'two'))
        self.assertSequenceEqual(new_table.columns['one'], (2,))

class TestTableAggregate(unittest.TestCase):
    def setUp(self):
        self.rows = (
            ('a', 2, 3, 4),
            (None, 3, 5, None),
            ('a', 2, 4, None),
            ('b', 3, 4, None)
        )

        self.column_types = (journalism.TextColumn, journalism.IntColumn, journalism.IntColumn, journalism.IntColumn)
        self.column_names = ('one', 'two', 'three', 'four')

    def test_aggregate_sum(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.aggregate('one', (('two', 'sum'), ))

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table._column_names, ('one', 'two'))
        self.assertSequenceEqual(new_table.rows[0], ('a', 4))
        self.assertSequenceEqual(new_table.rows[1], (None, 3))
        self.assertSequenceEqual(new_table.rows[2], ('b', 3))

    def test_aggregate_sum_two_columns(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.aggregate('one', (('two', 'sum'), ('four', 'sum')))

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table._column_names, ('one', 'two', 'four'))
        self.assertSequenceEqual(new_table.rows[0], ('a', 4, 4))
        self.assertSequenceEqual(new_table.rows[1], (None, 3, 0))
        self.assertSequenceEqual(new_table.rows[2], ('b', 3, 0))

    def test_aggregate_sum_invalid(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        with self.assertRaises(journalism.UnsupportedOperationError):
            table.aggregate('two', (('one', 'sum'), ))

class TestTableCompute(unittest.TestCase):
    def setUp(self):
        self.rows = (
            ('a', 2, 3, 4),
            (None, 3, 5, None),
            ('a', 2, 4, None),
            ('b', 3, 4, None)
        )

        self.column_types = (journalism.TextColumn, journalism.IntColumn, journalism.IntColumn, journalism.IntColumn)
        self.column_names = ('one', 'two', 'three', 'four')

        self.table = journalism.Table(self.rows, self.column_types, self.column_names)

    def test_compute(self):
        new_table = self.table.compute('test', journalism.IntColumn, lambda r: r['two'] + r['three'])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4) 
        self.assertEqual(len(new_table.columns), 5) 

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 5))
        self.assertSequenceEqual(new_table.columns['test'], (5, 8, 6, 7))

    def test_percent_change(self):
        new_table = self.table.percent_change('two', 'three', 'test')

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4) 
        self.assertEqual(len(new_table.columns), 5) 

        to_one_place = lambda d: d.quantize(Decimal('0.1'))

        self.assertEqual(new_table.rows[0], ('a', 2, 3, 4, Decimal('50.0')))
        self.assertEqual(to_one_place(new_table.columns['test'][0]), Decimal('50.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][1]), Decimal('66.7'))
        self.assertEqual(to_one_place(new_table.columns['test'][2]), Decimal('100.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][3]), Decimal('33.3'))

    def test_rank(self):
        new_table = self.table.rank(lambda r: r['two'], 'rank')

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 1))
        self.assertSequenceEqual(new_table.rows[1], (None, 3, 5, None, 3))
        self.assertSequenceEqual(new_table.rows[2], ('a', 2, 4, None, 1))
        self.assertSequenceEqual(new_table.rows[3], ('b', 3, 4, None, 3))

        self.assertSequenceEqual(new_table.columns['rank'], (1, 3, 1, 3))

    def test_rank2(self):
        new_table = self.table.rank(lambda r: r['one'], 'rank')

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 1))
        self.assertSequenceEqual(new_table.rows[1], (None, 3, 5, None, 4))
        self.assertSequenceEqual(new_table.rows[2], ('a', 2, 4, None, 1))
        self.assertSequenceEqual(new_table.rows[3], ('b', 3, 4, None, 3))

        self.assertSequenceEqual(new_table.columns['rank'], (1, 4, 1, 3))

class TestTableJoin(unittest.TestCase):
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

        self.column_types = (journalism.TextColumn, journalism.IntColumn, journalism.IntColumn)

        self.left = journalism.Table(self.left_rows, self.column_types, ('one', 'two', 'three'))
        self.right = journalism.Table(self.right_rows, self.column_types, ('four', 'five', 'six'))

    def test_inner_join(self):
        new_table = self.left.inner_join('one', self.right, 'four')

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 6)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', 1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', 2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', None, 2, 'c'))

    def test_inner_join2(self):
        new_table = self.left.inner_join('one', self.right, 'five')

        self.assertEqual(len(new_table.rows), 1)
        self.assertEqual(len(new_table.columns), 6)

        self.assertSequenceEqual(new_table.rows[0], (2, 3, 'b', None, 2, 'c'))

    def test_inner_join_func(self):
        new_table = self.left.inner_join(
            lambda left: '%i%s' % (left['two'], left['three']),
            self.right,
            lambda right: '%i%s' % (right['five'], right['six'])
        )

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 6)

    def test_left_outer_join(self):
        new_table = self.left.left_outer_join('one', self.right, 'four')

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 6)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', 1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', 2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', None, 2, 'c'))

    def test_left_outer_join2(self):
        new_table = self.left.left_outer_join('one', self.right, 'five')

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 6)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', None, None, None))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', None, 2, 'c'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', None, None, None))

    def test_left_outer_func(self):
        new_table = self.left.left_outer_join(
            lambda left: '%i%s' % (left['two'], left['three']),
            self.right,
            lambda right: '%i%s' % (right['five'], right['six'])
        )

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 6)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', 1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', 2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', None, 2, 'c'))

class TestTableData(unittest.TestCase):
    def setUp(self):
        self.rows = ( 
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )
        self.column_names = ['one', 'two', 'three']
        self.column_types = [journalism.IntColumn, journalism.IntColumn, journalism.TextColumn]

    def test_data_immutable(self):
        rows = [ 
            [1, 4, 'a'],
            [2, 3, 'b'],
            [None, 2, 'c']
        ]

        table = journalism.Table(rows, self.column_types, self.column_names)
        rows[0] = [2, 2, 2]
        self.assertSequenceEqual(table.rows[0], [1, 4, 'a'])

    def test_fork_preserves_data(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)
        table2 = table._fork(table._data)

        self.assertIs(table._data, table2._data)

    def test_where_preserves_rows(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)
        table2 = table.where(lambda r: r['one'] == 1)
        table3 = table2.where(lambda r: r['one'] == 1)

        self.assertIsNot(table._data[0], table2._data[0])
        self.assertIs(table2._data[0], table3._data[0])

    def test_order_by_preserves_rows(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)
        table2 = table.order_by(lambda r: r['one'])
        table3 = table2.order_by(lambda r: r['one'])

        self.assertIsNot(table._data[0], table2._data[0])
        self.assertIs(table2._data[0], table3._data[0])

    def test_limit_preserves_rows(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)
        table2 = table.limit(2)
        table3 = table2.limit(2)

        self.assertIsNot(table._data[0], table2._data[0])
        self.assertIs(table2._data[0], table3._data[0])

    def test_compute_creates_rows(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)
        table2 = table.compute('new2', journalism.IntColumn, lambda r: r['one'])
        table3 = table2.compute('new3', journalism.IntColumn, lambda r: r['one'])

        self.assertIsNot(table._data[0], table2._data[0])
        self.assertNotEqual(table._data[0], table2._data[0])
        self.assertIsNot(table2._data[0], table3._data[0])
        self.assertNotEqual(table2._data[0], table3._data[0])
        self.assertSequenceEqual(table._data[0], (1, 4, 'a'))

