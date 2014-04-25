#!/usr/bin/env python

import unittest2 as unittest

import journalism

class TestTable(unittest.TestCase):
    def setUp(self):
        self.rows = [
            [1, 2, 'a'],
            [2, 3, 'b'],
            [None, 4, 'c']
        ]
        self.column_names = ['one', 'two', 'three']
        self.column_types = [journalism.IntColumn, journalism.IntColumn, journalism.TextColumn]

    def test_create_table(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        self.assertEqual(len(table), 3)

        self.assertEqual(table[0], [1, 2, 'a'])
        self.assertEqual(table[1], [2, 3, 'b'])
        self.assertEqual(table[2], [None, 4, 'c'])

    def test_create_table_header(self):
        rows = [['one', 'two', 'three']]
        rows.extend(self.rows)

        table = journalism.Table(rows, self.column_types)

        self.assertEqual(table[0], [1, 2, 'a'])
        self.assertEqual(table[1], [2, 3, 'b'])
        self.assertEqual(table[2], [None, 4, 'c'])

    def test_filter(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.filter('one', [2, None])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table), 2)
        self.assertEqual(new_table[0], [2, 3, 'b'])

    def test_reject(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.reject('one', [2, None])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table), 1)
        self.assertEqual(new_table[0], [1, 2, 'a'])

class TestTableApplyOperations(unittest.TestCase):
    def setUp(self):
        self.rows = [
            [1, 2, 'a'],
            [2, 3, 'b'],
            [None, 4, 'c']
        ]
        self.column_names = ['one', 'two', 'three']
        self.column_types = [journalism.IntColumn, journalism.IntColumn, journalism.TextColumn]

    def test_sum(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        self.assertEqual(table.apply('one', journalism.ops.sum), 3) 

    def test_sum_invalid(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        with self.assertRaises(journalism.UnsupportedOperationError):
            table.apply('three', journalism.ops.sum)

class TestTableAggregate(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ['one', 'two', 'three', 'four'],
            ['a', 2, 3, 4],
            [None, 3, 5, None],
            ['a', 2, 4, None],
            ['b', 3, 4, None]
        ]

        self.column_types = [journalism.TextColumn, journalism.IntColumn, journalism.IntColumn, journalism.IntColumn]

    def test_aggregate_sum(self):
        table = journalism.Table(self.rows, self.column_types)

        new_table = table.aggregate('one', [('two', journalism.ops.sum)])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table), 3)
        self.assertEqual(new_table.column_names, ['one', 'two'])
        self.assertEqual(new_table[0], ['a', 4])
        self.assertEqual(new_table[1], [None, 3])
        self.assertEqual(new_table[2], ['b', 3])

    def test_aggregate_sum_two_columns(self):
        table = journalism.Table(self.rows, self.column_types)

        new_table = table.aggregate('one', [('two', journalism.ops.sum), ('four', journalism.ops.sum)])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table), 3)
        self.assertEqual(new_table.column_names, ['one', 'two', 'four'])
        self.assertEqual(new_table[0], ['a', 4, 4])
        self.assertEqual(new_table[1], [None, 3, 0])
        self.assertEqual(new_table[2], ['b', 3, 0])

    def test_aggregate_sum_invalid(self):
        table = journalism.Table(self.rows, self.column_types)

        with self.assertRaises(journalism.UnsupportedOperationError):
            table.aggregate('two', [('one', journalism.ops.sum)])

