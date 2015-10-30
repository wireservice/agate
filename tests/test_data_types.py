#!/usr/bin/env python
# -*- coding: utf8 -*-

import datetime
from decimal import Decimal

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import pytz

from agate.columns import *
from agate.data_types import *
from agate.exceptions import CastError
from agate.table import Table
from agate.tableset import TableSet

class TestText(unittest.TestCase):
    def setUp(self):
        self.type = Text()

    def test_test(self):
        self.assertEqual(self.type.test(None), True)
        self.assertEqual(self.type.test('N/A'), True)
        self.assertEqual(self.type.test(True), True)
        self.assertEqual(self.type.test('True'), True)
        self.assertEqual(self.type.test(1), True)
        self.assertEqual(self.type.test(Decimal('1')), True)
        self.assertEqual(self.type.test('2.7'), True)
        self.assertEqual(self.type.test(2.7), True)
        self.assertEqual(self.type.test('3/1/1994'), True)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), True)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), True)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), True)
        self.assertEqual(self.type.test('4:10'), True)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), True)
        self.assertEqual(self.type.test('a'), True)

    def test_cast(self):
        values = ('a', 1, None, Decimal('2.7'), 'n/a', u'👍')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, ('a', '1', None, '2.7', None, u'👍'))

class TestBoolean(unittest.TestCase):
    def setUp(self):
        self.type = Boolean()

    def test_test(self):
        self.assertEqual(self.type.test(None), True)
        self.assertEqual(self.type.test('N/A'), True)
        self.assertEqual(self.type.test(True), True)
        self.assertEqual(self.type.test('True'), True)
        self.assertEqual(self.type.test(1), False)
        self.assertEqual(self.type.test(Decimal('1')), False)
        self.assertEqual(self.type.test('2.7'), False)
        self.assertEqual(self.type.test(2.7), False)
        self.assertEqual(self.type.test('3/1/1994'), False)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), False)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), False)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), False)
        self.assertEqual(self.type.test('4:10'), False)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), False)
        self.assertEqual(self.type.test('a'), False)

    def test_cast(self):
        values = (True, 'yes', None, False, 'no', 'n/a')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (True, True, None, False, False, None))

    def test_cast_custom_strings(self):
        values = ('a', 'b', 'c', 'd', 'e', 'f')
        boolean_type = Boolean(
            true_values=('a', 'b'),
            false_values=('d', 'e'),
            null_values=('c', 'f')
        )
        casted = tuple(boolean_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (True, True, None, False, False, None))

    def test_cast_error(self):
        with self.assertRaises(CastError):
            self.type.cast('quack')

class TestNumber(unittest.TestCase):
    def setUp(self):
        self.type = Number()

    def test_test(self):
        self.assertEqual(self.type.test(None), True)
        self.assertEqual(self.type.test('N/A'), True)
        self.assertEqual(self.type.test(True), False)
        self.assertEqual(self.type.test('True'), False)
        self.assertEqual(self.type.test(1), True)
        self.assertEqual(self.type.test(Decimal('1')), True)
        self.assertEqual(self.type.test('2.7'), True)
        self.assertEqual(self.type.test(2.7), True)
        self.assertEqual(self.type.test('3/1/1994'), False)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), False)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), False)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), False)
        self.assertEqual(self.type.test('4:10'), False)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), False)
        self.assertEqual(self.type.test('a'), False)

    def test_cast(self):
        values = (2, 1, None, Decimal('2.7'), 'n/a', '2.7', '200,000,000')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (Decimal('2'), Decimal('1'), None, Decimal('2.7'), None, Decimal('2.7'), Decimal('200000000')))

    def test_currency_cast(self):
        values = ('$2.70', '$0.70', u'€14', u'75¢')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (Decimal('2.7'), Decimal('0.7'), Decimal('14'), Decimal('75')))

    def test_cast_locale(self):
        values = (2, 1, None, Decimal('2.7'), 'n/a', '2,7', '200.000.000')
        casted = tuple(Number(locale='de_DE').cast(v) for v in values)
        self.assertSequenceEqual(casted, (Decimal('2'), Decimal('1'), None, Decimal('2.7'), None, Decimal('2.7'), Decimal('200000000')))

    def test_cast_text(self):
        with self.assertRaises(CastError):
            self.type.cast('a')

    def test_cast_float(self):
        with self.assertRaises(CastError):
            self.type.cast(1.1)

    def test_cast_error(self):
        with self.assertRaises(CastError):
            self.type.cast('quack')

class TestDate(unittest.TestCase):
    def setUp(self):
        self.type = Date()

    def test_test(self):
        self.assertEqual(self.type.test(None), True)
        self.assertEqual(self.type.test('N/A'), True)
        self.assertEqual(self.type.test(True), False)
        self.assertEqual(self.type.test('True'), False)
        self.assertEqual(self.type.test(1), False)
        self.assertEqual(self.type.test(Decimal('1')), False)
        self.assertEqual(self.type.test('2.7'), False)
        self.assertEqual(self.type.test(2.7), False)
        self.assertEqual(self.type.test('3/1/1994'), True)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), True)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), False)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), False)
        self.assertEqual(self.type.test('4:10'), False)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), False)
        self.assertEqual(self.type.test('a'), False)

    def test_cast_format(self):
        date_type = Date(date_format='%m-%d-%Y')

        values = ('03-01-1994', '02-17-2011', None, '01-05-1984', 'n/a')
        casted = tuple(date_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.date(1994, 3, 1),
            datetime.date(2011, 2, 17),
            None,
            datetime.date(1984, 1, 5),
            None
        ))


    def test_cast_parser(self):
        values = ('3/1/1994', '2/17/2011', None, 'January 5th, 1984', 'n/a')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.date(1994, 3, 1),
            datetime.date(2011, 2, 17),
            None,
            datetime.date(1984, 1, 5),
            None
        ))

    @unittest.skip('Broken pending parsedatetime 1.6 release')
    def test_dash_format(self):
        values = ('1994-03-01', '2011-02-17')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.date(1994, 3, 1),
            datetime.date(2011, 2, 17)
        ))

    def test_cast_error(self):
        with self.assertRaises(CastError):
            self.type.cast('quack')

class TestDateTime(unittest.TestCase):
    def setUp(self):
        self.type = DateTime()

    def test_test(self):
        self.assertEqual(self.type.test(None), True)
        self.assertEqual(self.type.test('N/A'), True)
        self.assertEqual(self.type.test(True), False)
        self.assertEqual(self.type.test('True'), False)
        self.assertEqual(self.type.test(1), False)
        self.assertEqual(self.type.test(Decimal('1')), False)
        self.assertEqual(self.type.test('2.7'), False)
        self.assertEqual(self.type.test(2.7), False)
        self.assertEqual(self.type.test('3/1/1994'), False)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), False)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), True)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), True)
        self.assertEqual(self.type.test('4:10'), False)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), False)
        self.assertEqual(self.type.test('a'), False)

    def test_cast_format(self):
        datetime_type = DateTime(datetime_format='%m-%d-%Y %I:%M %p')

        values = ('03-01-1994 12:30 PM', '02-17-1011 06:30 AM', None, '01-05-1984 06:30 PM', 'n/a')
        casted = tuple(datetime_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0),
            datetime.datetime(1011, 2, 17, 6, 30, 0),
            None,
            datetime.datetime(1984, 1, 5, 18, 30, 0),
            None
        ))

    def test_cast_parser(self):
        values = ('3/1/1994 12:30 PM', '2/17/2011 06:30', None, 'January 5th, 1984 22:37', 'n/a')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0),
            datetime.datetime(2011, 2, 17, 6, 30, 0),
            None,
            datetime.datetime(1984, 1, 5, 22, 37, 0),
            None
        ))

    def test_cast_parser_timezone(self):
        tzinfo = pytz.timezone('US/Pacific')
        datetime_type = DateTime(timezone=tzinfo)

        values = ('3/1/1994 12:30 PM', '2/17/2011 06:30', None, 'January 5th, 1984 22:37', 'n/a')
        casted = tuple(datetime_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            tzinfo.localize(datetime.datetime(1994, 3, 1, 12, 30, 0, 0)),
            tzinfo.localize(datetime.datetime(2011, 2, 17, 6, 30, 0, 0)),
            None,
            tzinfo.localize(datetime.datetime(1984, 1, 5, 22, 37, 0, 0)),
            None
        ))

    def test_cast_error(self):
        with self.assertRaises(CastError):
            self.type.cast('quack')

class TestTimeDelta(unittest.TestCase):
    def setUp(self):
        self.type = TimeDelta()

    def test_test(self):
        self.assertEqual(self.type.test(None), True)
        self.assertEqual(self.type.test('N/A'), True)
        self.assertEqual(self.type.test(True), False)
        self.assertEqual(self.type.test('True'), False)
        self.assertEqual(self.type.test(1), False)
        self.assertEqual(self.type.test(Decimal('1')), False)
        self.assertEqual(self.type.test('2.7'), False)
        self.assertEqual(self.type.test(2.7), False)
        self.assertEqual(self.type.test('3/1/1994'), False)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), False)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), False)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), False)
        self.assertEqual(self.type.test('4:10'), True)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), True)
        self.assertEqual(self.type.test('a'), False)

    def test_cast_parser(self):
        values = ('4:10', '1.2m', '172 hours', '5 weeks, 2 days', 'n/a')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.timedelta(minutes=4, seconds=10),
            datetime.timedelta(minutes=1, seconds=12),
            datetime.timedelta(hours=172),
            datetime.timedelta(weeks=5, days=2),
            None
        ))


    def test_cast_error(self):
        with self.assertRaises(CastError):
            self.type.cast('quack')

class TestTypeTester(unittest.TestCase):
    def setUp(self):
        self.tester = TypeTester()

    def test_text_type(self):
        rows = [
            ('a',),
            ('b',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Text)

    def test_number_type(self):
        rows = [
            ('1.7',),
            ('200000000',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

    def test_number_locale(self):
        rows = [
            ('1,7',),
            ('200.000.000',),
            ('',)
        ]

        tester = TypeTester(locale='de_DE')
        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)
        self.assertEqual(inferred[0]._locale, 'de_DE')

    def test_number_percent(self):
        rows = [
            ('1.7%',),
            ('200000000%',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

    def test_number_currency(self):
        rows = [
            ('$1.7',),
            ('$200000000',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

    def test_number_currency_locale(self):
        rows = [
            (u'£1.7',),
            (u'£200000000',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

    def test_boolean_type(self):
        rows = [
            ('True',),
            ('FALSE',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Boolean)

    def test_date_type(self):
        rows = [
            ('5/7/1984',),
            ('2/28/1997',),
            ('3/19/2020',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Date)

    def test_date_time_type(self):
        rows = [
            ('5/7/84 3:44:12',),
            ('2/28/1997 3:12 AM',),
            ('3/19/20 4:40 PM',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], DateTime)

    def test_time_delta_type(self):
        rows = [
            ('1:42',),
            ('1w 27h',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], TimeDelta)

    def test_force_type(self):
        rows = [
            ('1.7',),
            ('200000000',),
            ('',)
        ]

        tester = TypeTester(force={
            'one': Text()
        })

        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Text)

    def test_limit(self):
        rows = [
            ('1.7',),
            ('foo',),
            ('',)
        ]

        tester = TypeTester(limit=1)
        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Number)

        tester = TypeTester(limit=2)
        inferred = tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0], Text)

    def test_table_from_csv(self):
        table = Table.from_csv('examples/test.csv', self.tester)

        self.assertSequenceEqual(table.column_names, ['one', 'two', 'three'])
        self.assertSequenceEqual(tuple(map(type, table.column_types)), [Number, Number, Text])

        self.assertEqual(len(table.columns), 3)

        self.assertSequenceEqual(table.rows[0], [1, 4, 'a'])
        self.assertSequenceEqual(table.rows[1], [2, 3, 'b'])
        self.assertSequenceEqual(table.rows[2], [None, 2, u'👍'])

    def test_tableset_from_csv(self):
        tableset = TableSet.from_csv('examples/tableset', column_types=self.tester)

        self.assertSequenceEqual(tableset.column_names, ['letter', 'number'])
        self.assertSequenceEqual(tuple(map(type, tableset.column_types)), [Text, Number])

        self.assertEqual(len(tableset['table1'].columns), 2)

        self.assertSequenceEqual(tableset['table1'].rows[0], ['a', 1])
        self.assertSequenceEqual(tableset['table1'].rows[1], ['a', 3])
        self.assertSequenceEqual(tableset['table1'].rows[2], ['b', 2])

    def test_tableset_from_csv_invalid_dir(self):
        with self.assertRaises(IOError):
            TableSet.from_csv('quack', self.tester)
