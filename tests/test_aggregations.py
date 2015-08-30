#!/usr/bin/env Python

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate import Table
from agate.aggregations import *
from agate.column_types import NumberType, TextType
from agate.exceptions import NullComputationError, UnsupportedAggregationError

class TestSimpleAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )

        self.number_type = NumberType()
        self.text_type = TextType()

        self.columns = (
            ('one', self.number_type),
            ('two', self.number_type),
            ('three', self.text_type)
        )

        self.table = Table(self.rows, self.columns)

    def test_any(self):
        self.assertEqual(self.table.columns['one'].aggregate(Any(lambda d: d == 2)), True)
        self.assertEqual(self.table.columns['one'].aggregate(Any(lambda d: d == 5)), False)

    def test_all(self):
        self.assertEqual(self.table.columns['one'].aggregate(All(lambda d: d != 5)), True)
        self.assertEqual(self.table.columns['one'].aggregate(All(lambda d: d == 2)), False)

    def test_count(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.columns)

        self.assertEqual(table.columns['one'].aggregate(Count(1)), 3)
        self.assertEqual(table.columns['one'].aggregate(Count(4)), 0)
        self.assertEqual(table.columns['one'].aggregate(Count(None)), 1)

class TestBooleanAggregation(unittest.TestCase):
    def test_any(self):
        column = BooleanColumn(None, 'one')
        column._data = lambda: (True, False, None)
        self.assertEqual(column.aggregate(Any()), True)

        column._data = lambda: (False, False, None)
        self.assertEqual(column.aggregate(Any()), False)

    def test_all(self):
        column = BooleanColumn(None, 'one')
        column._data = lambda: (True, True, None)
        self.assertEqual(column.aggregate(All()), False)

        column._data = lambda: (True, True, True)
        self.assertEqual(column.aggregate(All()), True)

class TestDateAggregation(unittest.TestCase):
    def test_min(self):
        column = DateColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            datetime.date(1984, 1, 5)
        )

        self.assertEqual(column.aggregate(Min()), datetime.date(1011, 2, 17))

    def test_max(self):
        column = DateColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            datetime.date(1984, 1, 5)
        )

        self.assertEqual(column.aggregate(Max()), datetime.date(1994, 3, 1))

class TestDateTimeAggregation(unittest.TestCase):
    def test_min(self):
        column = DateTimeColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.datetime(1994, 3, 3, 6, 31),
            datetime.datetime(1994, 3, 3, 6, 30, 30),
            datetime.datetime(1994, 3, 3, 6, 30)
        )

        self.assertEqual(column.aggregate(Min()), datetime.datetime(1994, 3, 3, 6, 30))

    def test_max(self):
        column = DateTimeColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.datetime(1994, 3, 3, 6, 31),
            datetime.datetime(1994, 3, 3, 6, 30, 30),
            datetime.datetime(1994, 3, 3, 6, 30)
        )

        self.assertEqual(column.aggregate(Max()), datetime.datetime(1994, 3, 3, 6, 31))

class TestNumberAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (Decimal('1.1'), Decimal('2.19'), 'a'),
            (Decimal('2.7'), Decimal('3.42'), 'b'),
            (None, Decimal('4.1'), 'c'),
            (Decimal('2.7'), Decimal('3.42'), 'c')
        )

        self.number_type = NumberType()
        self.text_type = TextType()

        self.columns = (
            ('one', self.number_type),
            ('two', self.number_type),
            ('three', self.text_type)
        )

        self.table = Table(self.rows, self.columns)

    def test_sum(self):
        self.assertEqual(self.table.columns['one'].aggregate(Sum()), Decimal('6.5'))
        self.assertEqual(self.table.columns['two'].aggregate(Sum()), Decimal('13.13'))

    def test_min(self):
        self.assertEqual(self.table.columns['one'].aggregate(Min()), Decimal('1.1'))
        self.assertEqual(self.table.columns['two'].aggregate(Min()), Decimal('2.19'))

    def test_max(self):
        self.assertEqual(self.table.columns['one'].aggregate(Max()), Decimal('2.7'))
        self.assertEqual(self.table.columns['two'].aggregate(Max()), Decimal('4.1'))

    def test_mean(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].aggregate(Mean())

        self.assertEqual(self.table.columns['two'].aggregate(Mean()), Decimal('3.2825'))

    def test_median(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].aggregate(Median())

        self.assertEqual(self.table.columns['two'].aggregate(Median()), Decimal('3.42'))

    def test_mode(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].aggregate(Mode())

        self.assertEqual(self.table.columns['two'].aggregate(Mode()), Decimal('3.42'))

    def test_iqr(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].aggregate(IQR())

        self.assertEqual(self.table.columns['two'].aggregate(IQR()), Decimal('0.955'))

    def test_variance(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].aggregate(Variance())

        self.assertEqual(self.table.columns['two'].aggregate(Variance()).quantize(Decimal('0.01')), Decimal('0.47'))

    def test_stdev(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].aggregate(StDev())

        self.assertAlmostEqual(self.table.columns['two'].aggregate(StDev()).quantize(Decimal('0.01')), Decimal('0.69'))

    def test_mad(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].aggregate(MAD())

        self.assertAlmostEqual(self.table.columns['two'].aggregate(MAD()), Decimal('0'))

class TestTextAggregation(unittest.TestCase):
    def test_max_length(self):
        column = TextColumn(None, 'one')
        column._data = lambda: ('a', 'gobble', 'wow')
        self.assertEqual(column.aggregate(MaxLength()), 6)
