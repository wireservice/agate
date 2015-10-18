#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six

from agate import Table
from agate.computations import Formula
from agate.data_types import *
from agate.rows import Row

class TestRow(unittest.TestCase):
    def setUp(self):
        self.column_names = ('one', 'two', 'three')
        self.data = (u'a', u'b', u'c')
        self.row = Row(self.column_names, self.data)

    def test_stringify(self):
        if six.PY2:
            self.assertEqual(str(self.row), "<agate.Row: (u'a', u'b', u'c')>")
        else:
            self.assertEqual(str(self.row), "<agate.Row: ('a', 'b', 'c')>")

    def test_stringify_long(self):
        column_names = ('one', 'two', 'three', 'four', 'five', 'six')
        data = (u'a', u'b', u'c', u'd', u'e', u'f')
        row = Row(column_names, data)

        if six.PY2:
            self.assertEqual(str(row), "<agate.Row: (u'a', u'b', u'c', u'd', u'e', ...)>")
        else:
            self.assertEqual(str(row), "<agate.Row: ('a', 'b', 'c', 'd', 'e', ...)>")

    def test_row_length(self):
        self.assertEqual(len(self.row), 3)

    def test_column_in_row(self):
        self.assertEqual(self.row['one'], 'a')
        self.assertEqual(self.row[0], 'a')

    def test_column_in_row_invalid(self):
        with self.assertRaises(KeyError):
            self.row['four']

        with self.assertRaises(IndexError):
            self.row[3]

    def test_immutable(self):
        with self.assertRaises(TypeError):
            self.row[0] = 'foo'

        with self.assertRaises(TypeError):
            self.row[0][0] = 100

    def test_get_cell(self):
        self.assertEqual(self.row['one'], 'a')
        self.assertEqual(self.row['two'], 'b')
        self.assertEqual(self.row['three'], 'c')

class TestRowSequence(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.columns = (
            ('one', self.number_type),
            ('two', self.number_type),
            ('three', self.text_type)
        )

        self.table = Table(self.rows, self.columns)

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

    def test_get_invalid_row(self):
        with self.assertRaises(IndexError):
            self.table.rows[3]

        with self.assertRaises(KeyError):
            self.table.rows['foo']

    def test_iterate_rows(self):
        it = iter(self.table.rows)

        self.assertSequenceEqual(next(it), (1, 2, 'a'))
        self.assertSequenceEqual(next(it), (2, 3, 'b'))
        self.assertSequenceEqual(next(it), (None, 4, 'c'))

        with self.assertRaises(StopIteration):
            next(it)

    def test_slice(self):
        s = self.table.rows[1:]

        self.assertEqual(len(s), 2)
        self.assertSequenceEqual(s[0], (2, 3, 'b'))
        self.assertSequenceEqual(s[1], (None, 4, 'c'))

    def test_slice_crazy(self):
        s = self.table.rows[:-2:-2]

        self.assertEqual(len(s), 1)
        self.assertSequenceEqual(s[0], (None, 4, 'c'))
