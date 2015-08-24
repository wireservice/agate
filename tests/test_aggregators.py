#!/usr/bin/env Python

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from journalism import Table
from journalism.aggregators import *
from journalism.column_types import NumberType, TextType
from journalism.exceptions import NullComputationError, UnsupportedAggregationError

class TestSimpleAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )
        self.column_names = ('one', 'two', 'three')
        self.number_type = NumberType()
        self.text_type = TextType()
        self.column_types = (self.number_type, self.number_type, self.text_type)

        self.table = Table(self.rows, self.column_types, self.column_names)

    def test_any(self):
        self.assertEqual(self.table.columns['one'].summarize(Any(lambda d: d == 2)), True)
        self.assertEqual(self.table.columns['one'].summarize(Any(lambda d: d == 5)), False)

    def test_all(self):
        self.assertEqual(self.table.columns['one'].summarize(All(lambda d: d != 5)), True)
        self.assertEqual(self.table.columns['one'].summarize(All(lambda d: d == 2)), False)

    def test_count(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.column_types, self.column_names)

        self.assertEqual(table.columns['one'].summarize(Count(1)), 3)
        self.assertEqual(table.columns['one'].summarize(Count(4)), 0)
        self.assertEqual(table.columns['one'].summarize(Count(None)), 1)

class TestBooleanAggregation(unittest.TestCase):
    def test_any(self):
        column = BooleanColumn(None, 'one')
        column._data = lambda: (True, False, None)
        self.assertEqual(column.summarize(Any()), True)

        column._data = lambda: (False, False, None)
        self.assertEqual(column.summarize(Any()), False)

    def test_all(self):
        column = BooleanColumn(None, 'one')
        column._data = lambda: (True, True, None)
        self.assertEqual(column.summarize(All()), False)

        column._data = lambda: (True, True, True)
        self.assertEqual(column.summarize(All()), True)


class TestDateAggregation(unittest.TestCase):
    def test_min(self):
        column = DateColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            datetime.date(1984, 1, 5)
        )

        self.assertEqual(column.summarize(Min()), datetime.date(1011, 2, 17))

    def test_max(self):
        column = DateColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            datetime.date(1984, 1, 5)
        )

        self.assertEqual(column.summarize(Max()), datetime.date(1994, 3, 1))

class TestDateTimeAggregation(unittest.TestCase):
    def test_min(self):
        column = DateTimeColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.datetime(1994, 3, 3, 6, 31),
            datetime.datetime(1994, 3, 3, 6, 30, 30),
            datetime.datetime(1994, 3, 3, 6, 30)
        )

        self.assertEqual(column.summarize(Min()), datetime.datetime(1994, 3, 3, 6, 30))

    def test_max(self):
        column = DateTimeColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.datetime(1994, 3, 3, 6, 31),
            datetime.datetime(1994, 3, 3, 6, 30, 30),
            datetime.datetime(1994, 3, 3, 6, 30)
        )

        self.assertEqual(column.summarize(Max()), datetime.datetime(1994, 3, 3, 6, 31))

class TestNumberAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (Decimal('1.1'), Decimal('2.19'), 'a'),
            (Decimal('2.7'), Decimal('3.42'), 'b'),
            (None, Decimal('4.1'), 'c'),
            (Decimal('2.7'), Decimal('3.42'), 'c')
        )
        self.column_names = ('one', 'two', 'three')
        self.number_type = NumberType()
        self.text_type = TextType()
        self.column_types = (self.number_type, self.number_type, self.text_type)

        self.table = Table(self.rows, self.column_types, self.column_names)

    def test_sum(self):
        self.assertEqual(self.table.columns['one'].summarize(Sum()), Decimal('6.5'))
        self.assertEqual(self.table.columns['two'].summarize(Sum()), Decimal('13.13'))

    def test_min(self):
        self.assertEqual(self.table.columns['one'].summarize(Min()), Decimal('1.1'))
        self.assertEqual(self.table.columns['two'].summarize(Min()), Decimal('2.19'))

    def test_max(self):
        self.assertEqual(self.table.columns['one'].summarize(Max()), Decimal('2.7'))
        self.assertEqual(self.table.columns['two'].summarize(Max()), Decimal('4.1'))

    def test_mean(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].summarize(Mean())

        self.assertEqual(self.table.columns['two'].summarize(Mean()), Decimal('3.2825'))

    def test_median(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].summarize(Median())

        self.assertEqual(self.table.columns['two'].summarize(Median()), Decimal('3.42'))

    def test_mode(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].summarize(Mode())

        self.assertEqual(self.table.columns['two'].summarize(Mode()), Decimal('3.42'))

    def test_iqr(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].summarize(IQR())

        print self.table.columns['two'].quartiles()

        self.assertEqual(self.table.columns['two'].summarize(IQR()), Decimal('0.955'))

    def test_variance(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].summarize(Variance())

        self.assertEqual(self.table.columns['two'].summarize(Variance()).quantize(Decimal('0.01')), Decimal('0.47'))

    def test_stdev(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].summarize(StDev())

        self.assertAlmostEqual(self.table.columns['two'].summarize(StDev()).quantize(Decimal('0.01')), Decimal('0.69'))

    def test_mad(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].summarize(MAD())

        self.assertAlmostEqual(self.table.columns['two'].summarize(MAD()), Decimal('0'))

class TestTextAggregation(unittest.TestCase):
    def test_max_length(self):
        column = TextColumn(None, 'one')
        column._data = lambda: ('a', 'gobble', 'wow')
        self.assertEqual(column.summarize(MaxLength()), 6)
