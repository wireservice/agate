#!/usr/bin/env python

import unittest2 as unittest

import journalism

class TestRows(unittest.TestCase):
    def setUp(self):
        self.rows = [
            [1, 2, 'a'],
            [2, 3, 'b'],
            [None, 4, 'c']
        ]
        self.column_names = ['one', 'two', 'three']
        self.column_types = [journalism.IntColumn, journalism.IntColumn, journalism.TextColumn]
        
        self.table = journalism.Table(self.rows, self.column_types, self.column_names)

    def test_length(self):
        self.assertEqual(len(self.table.rows), 3)

    def test_get_row(self):
        self.assertEqual(self.table.rows[0], [1, 2, 'a'])
        self.assertEqual(self.table.rows[1], [2, 3, 'b'])

    def test_get_row_cached(self):
        r = self.table.rows[0]
        r2 = self.table.rows[0]
        r3 = self.table.rows[1]

        self.assertIs(r, r2)
        self.assertIsNot(r, r3)

    def test_get_invalid_column(self):
        with self.assertRaises(IndexError):
            self.table.rows[3]

    def test_row_length(self):
        self.assertEqual(len(self.table.rows[0]), 3)

    def test_iterate_rows(self):
        it = iter(self.table.rows)
        
        self.assertEqual(it.next(), [1, 2, 'a'])
        self.assertEqual(it.next(), [2, 3, 'b'])
        self.assertEqual(it.next(), [None, 4, 'c'])

        with self.assertRaises(StopIteration):
            it.next()

    def test_immutable(self):
        with self.assertRaises(TypeError):
            self.table.rows[0] = 'foo'

        with self.assertRaises(TypeError):
            self.table.rows[0][0] = 100

    def test_get_cell(self):
        self.assertEqual(self.table.rows[0]['one'], 1)
        self.assertEqual(self.table.rows[1]['two'], 3)
        self.assertEqual(self.table.rows[2]['three'], 'c')

    def test_slice(self):
        s = self.table.rows[1:]

        self.assertEqual(len(s), 2)
        self.assertEqual(s[0], [2, 3, 'b'])
        self.assertEqual(s[1], [None, 4, 'c'])

    def test_slice_crazy(self):
        s = self.table.rows[:-2:-2]

        self.assertEqual(len(s), 1)
        self.assertEqual(s[0], [None, 4, 'c'])

