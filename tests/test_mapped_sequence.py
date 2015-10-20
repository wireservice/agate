#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six

from agate import Table
from agate.computations import Formula
from agate.data_types import *
from agate.mapped_sequence import MappedSequence

class TestMappedSequence(unittest.TestCase):
    def setUp(self):
        self.column_names = ('one', 'two', 'three')
        self.data = (u'a', u'b', u'c')
        self.row = MappedSequence(self.data, self.column_names)

    def test_stringify(self):
        if six.PY2:
            self.assertEqual(str(self.row), "<agate.MappedSequence: (u'a', u'b', u'c')>")
        else:
            self.assertEqual(str(self.row), "<agate.MappedSequence: ('a', 'b', 'c')>")

    def test_stringify_long(self):
        column_names = ('one', 'two', 'three', 'four', 'five', 'six')
        data = (u'a', u'b', u'c', u'd', u'e', u'f')
        row = MappedSequence(data, column_names)

        if six.PY2:
            self.assertEqual(str(row), "<agate.MappedSequence: (u'a', u'b', u'c', u'd', u'e', ...)>")
        else:
            self.assertEqual(str(row), "<agate.MappedSequence: ('a', 'b', 'c', 'd', 'e', ...)>")

    def test_length(self):
        self.assertEqual(len(self.row), 3)

    def test_is_immutable(self):
        with self.assertRaises(TypeError):
            self.row[0] = 'foo'

        with self.assertRaises(TypeError):
            self.row['one'] = 100

    def test_get_item(self):
        self.assertEqual(self.row['one'], 'a')
        self.assertEqual(self.row['two'], 'b')
        self.assertEqual(self.row['three'], 'c')

    def test_get_by_key(self):
        self.assertEqual(self.row['one'], 'a')
        self.assertEqual(self.row[0], 'a')

    def test_get_by_slice(self):
        self.assertSequenceEqual(self.row[1:], ('b', 'c'))

    def test_get_invalid(self):
        with self.assertRaises(IndexError):
            self.row[3]

        with self.assertRaises(KeyError):
            self.row['foo']

    def test_iterate(self):
        it = iter(self.row)

        self.assertSequenceEqual(next(it), 'a')
        self.assertSequenceEqual(next(it), 'b')
        self.assertSequenceEqual(next(it), 'c')

        with self.assertRaises(StopIteration):
            next(it)
