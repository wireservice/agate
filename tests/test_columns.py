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

class TestIntColumn(unittest.TestCase):
    def setUp(self):
        self.rows = [
            [1, 2, 'a'],
            [2, 3, 'b'],
            [None, 4, 'c'],
            [2, 1, 'c']
        ]
        self.column_names = ['one', 'two', 'three']
        self.column_types = [journalism.IntColumn, journalism.IntColumn, journalism.TextColumn]
        
        self.table = journalism.Table(self.rows, self.column_types, self.column_names)

    def test_validate(self):
        # TODO
        pass

    def test_sum(self):
        self.assertEqual(self.table.columns['one'].sum(), 5)
        self.assertEqual(self.table.columns['two'].sum(), 10)

    def test_min(self):
        self.assertEqual(self.table.columns['one'].min(), 1)
        self.assertEqual(self.table.columns['two'].min(), 1)

    def test_max(self):
        self.assertEqual(self.table.columns['one'].max(), 2)
        self.assertEqual(self.table.columns['two'].max(), 4)

    def test_median(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].median()

        self.assertEqual(self.table.columns['two'].median(), 2.5)

    def test_mode(self):
        pass

    def test_stdev(self):
        pass

class TestFloatColumn(unittest.TestCase):
    def setUp(self):
        self.rows = [
            [1.1, 2.19, 'a'],
            [2.7, 3.42, 'b'],
            [None, 4.1, 'c'],
            [2.7, 1, 'c']
        ]
        self.column_names = ['one', 'two', 'three']
        self.column_types = [journalism.FloatColumn, journalism.FloatColumn, journalism.TextColumn]
        
        self.table = journalism.Table(self.rows, self.column_types, self.column_names)

    def test_validate(self):
        # TODO
        pass

    def test_sum(self):
        self.assertEqual(self.table.columns['one'].sum(), 6.5)
        self.assertEqual(self.table.columns['two'].sum(), 10.71)

