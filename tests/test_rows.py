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

    def test_get_invalid_column(self):
        with self.assertRaises(IndexError):
            self.table.rows[3]

    def test_row_length(self):
        self.assertEqual(len(self.table.rows[0]), 3)

    def test_get_row_item(self):
        self.assertEqual(self.table.rows[0][1], 2)

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
