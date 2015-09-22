#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate.data_types import Text
from agate.table import Table
from agate.utils import Patchable, Quantiles

class TryPatch(object):
    def test(self, n):
        return n

    @classmethod
    def testcls(cls, n):
        return n

class TestMonkeyPatching(unittest.TestCase):
    def test_monkeypatch(self):
        before_table = Table([], [('foo', Text())])

        Table.monkeypatch(TryPatch)

        after_table = Table([], [('foo', Text())])

        self.assertIsNotNone(getattr(before_table, 'test'))
        self.assertIsNotNone(getattr(before_table, 'testcls'))

        self.assertIsNotNone(getattr(after_table, 'test'))
        self.assertIsNotNone(getattr(after_table, 'testcls'))

        self.assertEqual(before_table.test(5), 5)
        self.assertEqual(after_table.test(5), 5)
        self.assertEqual(Table.testcls(5), 5)

class TestQuantiles(unittest.TestCase):
    def setUp(self):
        self.values = [0, 10, 20, 30, 40, 50]
        self.quantiles = Quantiles(self.values)

    def test_methods(self):
        self.assertEqual(len(self.quantiles), 6)
        self.assertEqual(self.quantiles[2], 20)
        self.assertSequenceEqual(list(self.quantiles), self.values)
        self.assertEqual(repr(self.quantiles), repr(self.values))

    def test_locate(self):
        self.assertEqual(self.quantiles.locate(25), 2)
        self.assertEqual(self.quantiles.locate(40), 4)

        with self.assertRaises(ValueError):
            self.quantiles.locate(-10)

        with self.assertRaises(ValueError):
            self.quantiles.locate(51)
