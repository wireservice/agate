#!/usr/bin/env python

try:
    from cdecimal import Decimal, ROUND_FLOOR
except ImportError: #pragma: no cover
    from decimal import Decimal, ROUND_FLOOR

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate.data_types import Text
from agate.table import Table
from agate.utils import Patchable, Quantiles, round_to_magnitude

class TryPatch(object):
    def test(self, n):
        return n

    @classmethod
    def testcls(cls, n):
        return n

class TryPatchShadow(object):
    def __init__(self):
        self.foo = 'foo'

    def _get_row_count(self):
        return 1111

class TestMonkeyPatching(unittest.TestCase):
    def test_monkeypatch(self):
        before_table = Table([], [('foo', Text())])

        Table.monkeypatch(TryPatch)

        after_table = Table([], [('foo', Text())])

        self.assertSequenceEqual(Table.__bases__, [Patchable, TryPatch])

        self.assertIsNotNone(getattr(before_table, 'test'))
        self.assertIsNotNone(getattr(before_table, 'testcls'))

        self.assertIsNotNone(getattr(after_table, 'test'))
        self.assertIsNotNone(getattr(after_table, 'testcls'))

        self.assertEqual(before_table.test(5), 5)
        self.assertEqual(after_table.test(5), 5)
        self.assertEqual(Table.testcls(5), 5)

    def test_monkeypatch_shadow(self):
        before_table = Table([], [('foo', Text())])

        Table.monkeypatch(TryPatchShadow)

        after_table = Table([], [('foo', Text())])

        self.assertEqual(before_table._get_row_count(), 0)
        self.assertEqual(after_table._get_row_count(), 0)

        with self.assertRaises(AttributeError):
            after_table.foo == 'foo'

    def test_monkeypatch_double(self):
        Table.monkeypatch(TryPatch)
        Table.monkeypatch(TryPatch)
        Table.monkeypatch(TryPatch)

        self.assertSequenceEqual(Table.__bases__, [Patchable, TryPatch])

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

class TestMisc(unittest.TestCase):
    def test_round_to_magnitude(self):
        self.assertEqual(round_to_magnitude(Decimal('2.7')), Decimal('3'))
        self.assertEqual(round_to_magnitude(Decimal('-2.7'), rounding=ROUND_FLOOR), Decimal('-3'))
        self.assertEqual(round_to_magnitude(Decimal('2.2')), Decimal('3'))
        self.assertEqual(round_to_magnitude(Decimal('-2.2'), rounding=ROUND_FLOOR), Decimal('-3'))
        self.assertEqual(round_to_magnitude(Decimal('2.77')), Decimal('3'))
        self.assertEqual(round_to_magnitude(Decimal('-2.77'), rounding=ROUND_FLOOR), Decimal('-3'))
        self.assertEqual(round_to_magnitude(Decimal('2.22')), Decimal('3'))
        self.assertEqual(round_to_magnitude(Decimal('-2.22'), rounding=ROUND_FLOOR), Decimal('-3'))
        self.assertEqual(round_to_magnitude(Decimal('27')), Decimal('30'))
        self.assertEqual(round_to_magnitude(Decimal('-27'), rounding=ROUND_FLOOR), Decimal('-30'))
        self.assertEqual(round_to_magnitude(Decimal('22')), Decimal('30'))
        self.assertEqual(round_to_magnitude(Decimal('-22'), rounding=ROUND_FLOOR), Decimal('-30'))
        self.assertEqual(round_to_magnitude(Decimal('0.2')), Decimal('0.2'))
        self.assertEqual(round_to_magnitude(Decimal('-0.2'), rounding=ROUND_FLOOR), Decimal('-0.2'))
        self.assertEqual(round_to_magnitude(Decimal('0.22')), Decimal('0.3'))
        self.assertEqual(round_to_magnitude(Decimal('-0.22'), rounding=ROUND_FLOOR), Decimal('-0.3'))
        self.assertEqual(round_to_magnitude(Decimal('0.222')), Decimal('0.3'))
        self.assertEqual(round_to_magnitude(Decimal('-0.222'), rounding=ROUND_FLOOR), Decimal('-0.3'))
