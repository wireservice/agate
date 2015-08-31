#!/usr/bin/env python

import datetime

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate import Table
from agate.column_types import *
from agate.columns import *
from agate.exceptions import *

class TestColumnTypes(unittest.TestCase):
    def test_text(self):
        self.assertIsInstance(TextType()._create_column(None, 1), TextColumn)

    def test_text_cast(self):
        values = ('a', 1, None, Decimal('2.7'), 'n/a')
        casted = tuple(TextType().cast(v) for v in values)
        self.assertSequenceEqual(casted, ('a', '1', None, '2.7', None))

    def test_boolean(self):
        self.assertIsInstance(BooleanType()._create_column(None, 1), BooleanColumn)

    def test_boolean_cast(self):
        values = (True, 'yes', None, False, 'no', 'n/a')
        casted = tuple(BooleanType().cast(v) for v in values)
        self.assertSequenceEqual(casted, (True, True, None, False, False, None))

    def test_number(self):
        self.assertIsInstance(NumberType()._create_column(None, 1), NumberColumn)

    def test_number_cast(self):
        values = (2, 1, None, Decimal('2.7'), 'n/a')
        casted = tuple(NumberType().cast(v) for v in values)
        self.assertSequenceEqual(casted, (Decimal('2'), Decimal('1'), None, Decimal('2.7'), None))

    def test_number_cast_text(self):
        with self.assertRaises(CastError):
            NumberType().cast('a')

    def test_number_cast_float(self):
        with self.assertRaises(CastError):
            NumberType().cast(1.1)

    def test_date(self):
        self.assertIsInstance(DateType()._create_column(None, 1), DateColumn)

    def test_date_cast_format(self):
        date_type = DateType(date_format='%m-%d-%Y')

        values = ('03-01-1994', '02-17-1011', None, '01-05-1984', 'n/a')
        casted = tuple(date_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            None,
            datetime.date(1984, 1, 5),
            None
        ))

    def test_date_cast_parser(self):
        values = ('3-1-1994', '2/17/1011', None, 'January 5th, 1984', 'n/a')
        casted = tuple(DateType().cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            None,
            datetime.date(1984, 1, 5),
            None
        ))

    def test_datetime(self):
        self.assertIsInstance(DateTimeType()._create_column(None, 1), DateTimeColumn)

    def test_datetime_cast_format(self):
        datetime_type = DateTimeType(datetime_format='%m-%d-%Y %I:%M %p')

        values = ('03-01-1994 12:30 PM', '02-17-1011 06:30 AM', None, '01-05-1984 06:30 PM', 'n/a')
        casted = tuple(datetime_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0),
            datetime.datetime(1011, 2, 17, 6, 30, 0),
            None,
            datetime.datetime(1984, 1, 5, 18, 30, 0),
            None
        ))

    def test_datetime_cast_parser(self):
        values = ('3-1-1994 12:30 PM', '2/17/1011 06:30', None, 'January 5th, 1984 22:37', 'n/a')
        casted = tuple(DateTimeType().cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0),
            datetime.datetime(1011, 2, 17, 6, 30, 0),
            None,
            datetime.datetime(1984, 1, 5, 22, 37, 0),
            None
        ))

    def test_timedelta(self):
        self.assertIsInstance(TimeDeltaType()._create_column(None, 1), TimeDeltaColumn)

    def test_timedelta_cast_parser(self):
        values = ('4:10', '1.2m', '172 hours', '5 weeks, 2 days', 'n/a')
        casted = tuple(TimeDeltaType().cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.timedelta(minutes=4, seconds=10),
            datetime.timedelta(minutes=1, seconds=12),
            datetime.timedelta(hours=172),
            datetime.timedelta(weeks=5, days=2),
            None
        ))

class TestColumns(unittest.TestCase):
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

    def test_stringify(self):
        self.assertEqual(str(self.table.columns['one']), "<agate.columns.NumberColumn: (1, 2, None)>")

    def test_stringify_long(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )

        self.table = Table(rows, self.columns)

        self.assertEqual(str(self.table.columns['one']), "<agate.columns.NumberColumn: (1, 2, None, 1, 2, ...)>")

    def test_length(self):
        self.assertEqual(len(self.table.columns), 3)

    def test_get_column_data(self):
        self.assertSequenceEqual(self.table.columns['one'].get_data(), (1, 2, None))

    def test_get_column(self):
        self.assertSequenceEqual(self.table.columns['one'], (1, 2, None))

    def test_get_column_cached(self):
        c = self.table.columns['one']
        c2 = self.table.columns['one']
        c3 = self.table.columns['two']

        self.assertIs(c, c2)
        self.assertIsNot(c2, c3)

    def test_get_invalid_column(self):
        with self.assertRaises(ColumnDoesNotExistError):
            self.table.columns['four']

    def test_column_length(self):
        self.assertEqual(len(self.table.columns['one']), 3)

    def test_get_column_item(self):
        self.assertEqual(self.table.columns['one'][1], 2)

    def test_column_contains(self):
        self.assertEqual(1 in self.table.columns['one'], True)
        self.assertEqual(3 in self.table.columns['one'], False)

    def test_iterate_columns(self):
        it = iter(self.table.columns)

        self.assertSequenceEqual(next(it), (1, 2, None))
        self.assertSequenceEqual(next(it), (2, 3, 4))
        self.assertSequenceEqual(next(it), ('a', 'b', 'c'))

        with self.assertRaises(StopIteration):
            next(it)

    def test_immutable(self):
        with self.assertRaises(TypeError):
            self.table.columns['one'] = 'foo'

        with self.assertRaises(TypeError):
            self.table.columns['one'][0] = 100

    def test_percentiles(self):
        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, (('ints', self.number_type),))

        percentiles = table.columns['ints'].percentiles()

        self.assertEqual(percentiles[0], Decimal('1'))
        self.assertEqual(percentiles[25], Decimal('250.5'))
        self.assertEqual(percentiles[50], Decimal('500.5'))
        self.assertEqual(percentiles[75], Decimal('750.5'))
        self.assertEqual(percentiles[99], Decimal('990.5'))
        self.assertEqual(percentiles[100], Decimal('1000'))

    def test_percentiles_locate(self):
        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, (('ints', self.number_type),))

        percentiles = table.columns['ints'].percentiles()

        self.assertEqual(percentiles.locate(251), Decimal('25'))
        self.assertEqual(percentiles.locate(260), Decimal('25'))
        self.assertEqual(percentiles.locate(261), Decimal('26'))

        with self.assertRaises(ValueError):
            percentiles.locate(0)

        with self.assertRaises(ValueError):
            percentiles.locate(1012)

    def test_quartiles(self):
        """
        CDF quartile tests from:
        http://www.amstat.org/publications/jse/v14n3/langford.html#Parzen1979
        """
        # N = 4
        rows = [(n,) for n in [1, 2, 3, 4]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        for i, v in enumerate(['1', '1.5', '2.5', '3.5', '4']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 5
        rows = [(n,) for n in [1, 2, 3, 4, 5]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        for i, v in enumerate(['1', '2', '3', '4', '5']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 6
        rows = [(n,) for n in [1, 2, 3, 4, 5, 6]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        for i, v in enumerate(['1', '2', '3.5', '5', '6']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 7
        rows = [(n,) for n in [1, 2, 3, 4, 5, 6, 7]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        for i, v in enumerate(['1', '2', '4', '6', '7']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 8 (doubled)
        rows = [(n,) for n in [1, 1, 2, 2, 3, 3, 4, 4]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        for i, v in enumerate(['1', '1.5', '2.5', '3.5', '4']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 10 (doubled)
        rows = [(n,) for n in [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        for i, v in enumerate(['1', '2', '3', '4', '5']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 12 (doubled)
        rows = [(n,) for n in [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        for i, v in enumerate(['1', '2', '3.5', '5', '6']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 14 (doubled)
        rows = [(n,) for n in [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        for i, v in enumerate(['1', '2', '4', '6', '7']):
            self.assertEqual(quartiles[i], Decimal(v))

    def test_quartiles_locate(self):
        """
        CDF quartile tests from:
        http://www.amstat.org/publications/jse/v14n3/langford.html#Parzen1979
        """
        # N = 4
        rows = [(n,) for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]

        table = Table(rows, (('ints', self.number_type),))

        quartiles = table.columns['ints'].quartiles()

        self.assertEqual(quartiles.locate(2), Decimal('0'))
        self.assertEqual(quartiles.locate(4), Decimal('1'))
        self.assertEqual(quartiles.locate(6), Decimal('2'))
        self.assertEqual(quartiles.locate(8), Decimal('3'))

        with self.assertRaises(ValueError):
            quartiles.locate(0)

        with self.assertRaises(ValueError):
            quartiles.locate(11)

    def test_percentile_no_data(self):
        rows = (())

        table = Table(rows, (('ints', self.number_type),))

        with self.assertRaises(ValueError):
            table.columns['ints'].quartiles()
