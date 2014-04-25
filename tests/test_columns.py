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

    def test_map(self):
        def f(x):
            return x + 1 if x is not None else x

        new_table = self.table.columns['one'].map(f) 

        self.assertIsNot(new_table, self.table)
        self.assertEqual(self.table.columns['one'], [1, 2, None])
        self.assertEqual(self.table.rows[0], [1, 2, 'a'])

        self.assertEqual(new_table.columns['one'], [2, 3, None])
        self.assertEqual(new_table.rows[0], [2, 2, 'a'])

    def test_map_change_type(self):
        def f(x):
            return x + 1.1 if x is not None else x

        new_table = self.table.columns['one'].map(f, journalism.FloatColumn) 

        self.assertIsNot(new_table, self.table)
        self.assertEqual(self.table._column_types, [journalism.IntColumn, journalism.IntColumn, journalism.TextColumn])
        self.assertEqual(self.table.columns['one'], [1, 2, None])
        self.assertEqual(self.table.rows[0], [1, 2, 'a'])

        self.assertEqual(new_table._column_types, [journalism.FloatColumn, journalism.IntColumn, journalism.TextColumn])
        self.assertEqual(new_table.columns['one'], [2.1, 3.1, None])
        self.assertEqual(new_table.rows[0], [2.1, 2, 'a'])

    def test_map_change_name(self):
        new_table = self.table.columns['one'].map(lambda d: d, new_column_name='test') 

        self.assertIsNot(new_table, self.table)
        self.assertEqual(self.table._column_names, ['one', 'two', 'three'])
        self.assertEqual(new_table._column_names, ['test', 'two', 'three'])

class TestTextColumn(unittest.TestCase):
    def test_validate(self):
        column = journalism.TextColumn(None, 'one')
        column._data = lambda: ['a', 'b', 'c'] 
        column.validate()

        column._data = lambda: ['a', 'b', 3]

        with self.assertRaises(journalism.ColumnValidationError):
            column.validate()

    def test_cast(self):
        # TODO
        pass

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
        column = journalism.IntColumn(None, 'one')
        column._data = lambda: [1, 2, 3] 
        column.validate()

        column._data = lambda: [1, 'a', 3]

        with self.assertRaises(journalism.ColumnValidationError):
            column.validate()

    def test_cast(self):
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
        # TODO
        pass

    def test_stdev(self):
        # TODO
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
        column = journalism.FloatColumn(None, 'one')
        column._data = lambda: [1.0, 2.1, 3.3] 
        column.validate()

        column._data = lambda: [1.0, 'a', 3.3]

        with self.assertRaises(journalism.ColumnValidationError):
            column.validate()

        column._data = lambda: [1, 'a', 3.3]

        with self.assertRaises(journalism.ColumnValidationError):
            column.validate()

    def test_cast(self):
        # TODO
        pass

    def test_sum(self):
        self.assertEqual(self.table.columns['one'].sum(), 6.5)
        self.assertEqual(self.table.columns['two'].sum(), 10.71)

    def test_min(self):
        self.assertEqual(self.table.columns['one'].min(), 1.1)
        self.assertEqual(self.table.columns['two'].min(), 1)

    def test_max(self):
        self.assertEqual(self.table.columns['one'].max(), 2.7)
        self.assertEqual(self.table.columns['two'].max(), 4.1)

    def test_median(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].median()

        self.assertEqual(self.table.columns['two'].median(), 2.805)

    def test_mode(self):
        # TODO
        pass

    def test_stdev(self):
        # TODO
        pass

