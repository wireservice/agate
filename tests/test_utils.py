import unittest
from decimal import Decimal

from agate.utils import Quantiles, letter_name, round_limits


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
    def test_round_limits(self):
        self.assertEqual(
            round_limits(Decimal('-2.7'), Decimal('2.7')),
            (Decimal('-3'), Decimal('3'))
        )
        self.assertEqual(
            round_limits(Decimal('-2.2'), Decimal('2.2')),
            (Decimal('-3'), Decimal('3'))
        )
        self.assertEqual(
            round_limits(Decimal('-2.22'), Decimal('2.22')),
            (Decimal('-3'), Decimal('3'))
        )
        self.assertEqual(
            round_limits(Decimal('0'), Decimal('75')),
            (Decimal('0'), Decimal('80'))
        )
        self.assertEqual(
            round_limits(Decimal('45'), Decimal('300')),
            (Decimal('0'), Decimal('300'))
        )
        self.assertEqual(
            round_limits(Decimal('200.75'), Decimal('715.345')),
            (Decimal('200'), Decimal('800'))
        )
        self.assertEqual(
            round_limits(Decimal('0.75'), Decimal('0.800')),
            (Decimal('0'), Decimal('1'))
        )
        self.assertEqual(
            round_limits(Decimal('-0.505'), Decimal('0.47')),
            (Decimal('-0.6'), Decimal('0.5'))
        )

    def test_letter_name(self):
        self.assertEqual(letter_name(0), 'a')
        self.assertEqual(letter_name(4), 'e')
        self.assertEqual(letter_name(25), 'z')
        self.assertEqual(letter_name(30), 'ee')
        self.assertEqual(letter_name(77), 'zzz')
