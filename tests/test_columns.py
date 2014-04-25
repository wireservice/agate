#!/usr/bin/env python

import unittest2 as unittest

import journalism

class TestColumns(unittest.TestCase):
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
        self.assertEqual(len(self.table.columns), 3)

    def test_get_column(self):
        self.assertEqual(self.table.columns['one'], [1, 2, None])

    def test_get_invalid_column(self):
        with self.assertRaises(KeyError):
            self.table.columns['four']

    def test_column_length(self):
        self.assertEqual(len(self.table.columns['one']), 3)

    def test_get_column_item(self):
        self.assertEqual(self.table.columns['one'][1], 2)

    def test_iterate_columns(self):
        it = iter(self.table.columns)
        
        self.assertEqual(it.next(), [1, 2, None])
        self.assertEqual(it.next(), [2, 3, 4])
        self.assertEqual(it.next(), ['a', 'b', 'c'])

        with self.assertRaises(StopIteration):
            it.next()

    def test_immutable(self):
        with self.assertRaises(TypeError):
            self.table.columns['one'] = 'foo'

        with self.assertRaises(TypeError):
            self.table.columns['one'][0] = 100
