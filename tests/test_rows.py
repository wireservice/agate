#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import journalism

class TestRows(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )
        self.column_names = ('one', 'two', 'three')
        self.column_types = (journalism.IntColumn, journalism.IntColumn, journalism.TextColumn)
        
        self.table = journalism.Table(self.rows, self.column_types, self.column_names)

    def test_stringify(self):
        self.assertEqual(str(self.table.rows[0]), "<journalism.rows.Row: (1, 2, 'a')>")

    def test_stringify_long(self):
        rows = (
            (1, 2, 'a', 'b', 'c', 'd'),
        )
        
        self.table = journalism.Table(rows, self.column_types, self.column_names)

        self.assertEqual(str(self.table.rows[0]), "<journalism.rows.Row: (1, 2, 'a', 'b', 'c', ...)>")

    def test_length(self):
        self.assertEqual(len(self.table.rows), 3)

    def test_get_row(self):
        self.assertSequenceEqual(self.table.rows[0], (1, 2, 'a'))
        self.assertSequenceEqual(self.table.rows[1], (2, 3, 'b'))

    def test_get_row_cached(self):
        r = self.table.rows[0]
        r2 = self.table.rows[0]
        r3 = self.table.rows[1]

        self.assertIs(r, r2)
        self.assertIsNot(r, r3)

    def test_get_invalid_column(self):
        with self.assertRaises(journalism.RowDoesNotExistError):
            self.table.rows[3]

    def test_row_length(self):
        self.assertEqual(len(self.table.rows[0]), 3)

    def test_iterate_rows(self):
        it = iter(self.table.rows)
        
        self.assertSequenceEqual(next(it), (1, 2, 'a'))
        self.assertSequenceEqual(next(it), (2, 3, 'b'))
        self.assertSequenceEqual(next(it), (None, 4, 'c'))

        with self.assertRaises(StopIteration):
            next(it)

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
        self.assertSequenceEqual(s[0], (2, 3, 'b'))
        self.assertSequenceEqual(s[1], (None, 4, 'c'))

    def test_slice_crazy(self):
        s = self.table.rows[:-2:-2]

        self.assertEqual(len(s), 1)
        self.assertSequenceEqual(s[0], (None, 4, 'c'))

    def test_column_in_row(self):
        row = self.table.rows[0]

        self.assertEqual(row['one'], 1)

    def test_column_in_row_invalid(self):
        row = self.table.rows[0]

        with self.assertRaises(journalism.ColumnDoesNotExistError):
            row['four']

        with self.assertRaises(journalism.ColumnDoesNotExistError):
            row[3]
