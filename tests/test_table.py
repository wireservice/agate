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

        self.assertEqual(type(table['one']), journalism.IntColumn)
        self.assertEqual(type(table['two']), journalism.IntColumn)
        self.assertEqual(type(table['three']), journalism.TextColumn)

        self.assertEqual(list(table['one']), [1, 2, None])
        self.assertEqual(list(table['two']), [2, 3, 4])
        self.assertEqual(list(table['three']), ['a', 'b', 'c'])

    def test_create_table_header(self):
        rows = [['one', 'two', 'three']]
        rows.extend(self.rows)

        table = journalism.Table(rows, self.column_types)

        self.assertEqual(len(table), 3)

        self.assertEqual(type(table['one']), journalism.IntColumn)
        self.assertEqual(type(table['two']), journalism.IntColumn)
        self.assertEqual(type(table['three']), journalism.TextColumn)

        self.assertEqual(list(table['one']), [1, 2, None])
        self.assertEqual(list(table['two']), [2, 3, 4])
        self.assertEqual(list(table['three']), ['a', 'b', 'c'])

    def test_filter(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.filter('one', [2, None])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table), 3)
        self.assertEqual(list(new_table['one']), [2, None])

    def test_reject(self):
        table = journalism.Table(self.rows, self.column_types, self.column_names)

        new_table = table.reject('one', [2, None])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table), 3)
        self.assertEqual(list(new_table['one']), [1])
