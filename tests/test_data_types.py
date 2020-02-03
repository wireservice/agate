#!/usr/bin/env python
# -*- coding: utf8 -*-

import datetime
from decimal import Decimal
import pickle
import parsedatetime

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import pytz

from agate.columns import *
from agate.data_types import *
from agate.exceptions import CastError


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
        self.assertEqual(self.type.test('2015-01-01 02:34'), True)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), True)
        self.assertEqual(self.type.test('4:10'), True)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), True)
        self.assertEqual(self.type.test('a'), True)
        self.assertEqual(self.type.test('A\nB'), True)
        self.assertEqual(self.type.test(u'👍'), True)
        self.assertEqual(self.type.test('05_leslie3d_base'), True)
        self.assertEqual(self.type.test('2016-12-29'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30Z'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30+06:00'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30-06:00'), True)

    def test_cast(self):
        values = ('a', 1, None, Decimal('2.7'), 'n/a', u'👍', ' foo', 'foo ')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, ('a', '1', None, '2.7', None, u'👍', ' foo', 'foo '))

    def test_no_cast_nulls(self):
        values = ('', 'N/A', None)

        t = Text()
        casted = tuple(t.cast(v) for v in values)
        self.assertSequenceEqual(casted, (None, None, None))

        t = Text(cast_nulls=False)
        casted = tuple(t.cast(v) for v in values)
        self.assertSequenceEqual(casted, ('', 'N/A', None))


class TestBoolean(unittest.TestCase):
    def setUp(self):
        self.type = Boolean()

    def test_test(self):
        self.assertEqual(self.type.test(None), True)
        self.assertEqual(self.type.test('N/A'), True)
        self.assertEqual(self.type.test(True), True)
        self.assertEqual(self.type.test('True'), True)
        self.assertEqual(self.type.test('1'), True)
        self.assertEqual(self.type.test(1), True)
        self.assertEqual(self.type.test(Decimal('1')), True)
        self.assertEqual(self.type.test('0'), True)
        self.assertEqual(self.type.test(0), True)
        self.assertEqual(self.type.test(Decimal('0')), True)
        self.assertEqual(self.type.test('2.7'), False)
        self.assertEqual(self.type.test(2.7), False)
        self.assertEqual(self.type.test('3/1/1994'), False)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), False)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), False)
        self.assertEqual(self.type.test('2015-01-01 02:34'), False)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), False)
        self.assertEqual(self.type.test('4:10'), False)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), False)
        self.assertEqual(self.type.test('a'), False)
        self.assertEqual(self.type.test('A\nB'), False)
        self.assertEqual(self.type.test(u'👍'), False)
        self.assertEqual(self.type.test('05_leslie3d_base'), False)
        self.assertEqual(self.type.test('2016-12-29'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30Z'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30+06:00'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30-06:00'), False)

    def test_cast(self):
        values = (True, 'yes', None, False, 'no', 'n/a', '1', 0)
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (True, True, None, False, False, None, True, False))

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
        self.assertEqual(self.type.test('2015-01-01 02:34'), False)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), False)
        self.assertEqual(self.type.test('4:10'), False)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), False)
        self.assertEqual(self.type.test('a'), False)
        self.assertEqual(self.type.test('A\nB'), False)
        self.assertEqual(self.type.test(u'👍'), False)
        self.assertEqual(self.type.test('05_leslie3d_base'), False)
        self.assertEqual(self.type.test('2016-12-29'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30Z'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30+06:00'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30-06:00'), False)

    def test_cast(self):
        values = (2, 1, None, Decimal('2.7'), 'n/a', '2.7', '200,000,000')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (Decimal('2'), Decimal('1'), None, Decimal('2.7'), None, Decimal('2.7'), Decimal('200000000')))

    @unittest.skipIf(six.PY3, 'Not supported in Python 3.')
    def test_cast_long(self):
        self.assertEqual(self.type.test(long('141414')), True)
        self.assertEqual(self.type.cast(long('141414')), Decimal('141414'))

    def test_currency_cast(self):
        values = ('$2.70', '-$0.70', u'€14', u'50¢', u'-75¢', u'-$1,287')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (Decimal('2.7'), Decimal('-0.7'), Decimal('14'), Decimal('50'), Decimal('-75'), Decimal('-1287')))

    def test_cast_locale(self):
        values = (2, 1, None, Decimal('2.7'), 'n/a', '2,7', '200.000.000')
        casted = tuple(Number(locale='de_DE').cast(v) for v in values)
        self.assertSequenceEqual(casted, (Decimal('2'), Decimal('1'), None, Decimal('2.7'), None, Decimal('2.7'), Decimal('200000000')))

    def test_cast_text(self):
        with self.assertRaises(CastError):
            self.type.cast('a')

    def test_cast_floats(self):
        self.assertAlmostEqual(self.type.cast(0.1 + 0.2), Decimal('0.3'))
        self.assertEqual(self.type.cast(0.12345123456), Decimal('0.12345123456'))

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
        self.assertEqual(self.type.test('2.7'), True)
        self.assertEqual(self.type.test(2.7), False)
        self.assertEqual(self.type.test('3/1/1994'), True)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), True)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), False)
        self.assertEqual(self.type.test('2015-01-01 02:34'), False)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), False)
        self.assertEqual(self.type.test('4:10'), False)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), False)
        self.assertEqual(self.type.test('a'), False)
        self.assertEqual(self.type.test('A\nB'), False)
        self.assertEqual(self.type.test(u'👍'), False)
        self.assertEqual(self.type.test('05_leslie3d_base'), False)
        self.assertEqual(self.type.test('2016-12-29'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30Z'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30+06:00'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30-06:00'), False)
        self.assertEqual(self.type.test('MC 5.7.10 Per Dorothy Carroll'), False)
        self.assertEqual(self.type.test('testing workgroup fix - 4/7/2010 - Marcy Liberty'), False)

    def test_test_format(self):
        date_type = Date(date_format='%m-%d-%Y')

        self.assertEqual(date_type.test('3/1/1994'), False)
        self.assertEqual(date_type.test('03-01-1994'), True)
        self.assertEqual(date_type.test(datetime.date(1994, 3, 1)), True)

    def test_iso_format(self):
        values = ('1994-03-01', '2011-02-17')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.date(1994, 3, 1),
            datetime.date(2011, 2, 17)
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

    def test_cast_error(self):
        with self.assertRaises(CastError):
            self.type.cast('quack')

    def test_pickle_parser(self):
        from_pickle = pickle.loads(pickle.dumps(self.type))
        self.assertEqual(from_pickle.date_format, self.type.date_format)
        self.assertIsInstance(from_pickle.parser, parsedatetime.Calendar)


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
        self.assertEqual(self.type.test('2.7'), True)
        self.assertEqual(self.type.test(2.7), False)
        self.assertEqual(self.type.test('3/1/1994'), True)
        self.assertEqual(self.type.test(datetime.date(1994, 3, 1)), True)
        self.assertEqual(self.type.test('3/1/1994 12:30 PM'), True)
        self.assertEqual(self.type.test('2015-01-01 02:34'), True)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), True)
        self.assertEqual(self.type.test('4:10'), False)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), False)
        self.assertEqual(self.type.test('a'), False)
        self.assertEqual(self.type.test('A\nB'), False)
        self.assertEqual(self.type.test(u'👍'), False)
        self.assertEqual(self.type.test('05_leslie3d_base'), False)
        self.assertEqual(self.type.test('2016-12-29'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30Z'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30+06:00'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30-06:00'), True)
        self.assertEqual(self.type.test('720(38-4)31A-1.1(A)'), False)

    def test_test_format(self):
        datetime_type = DateTime(datetime_format='%m-%d-%Y %I:%M %p')

        self.assertEqual(datetime_type.test('3/1/1994 12:30 PM'), False)
        self.assertEqual(datetime_type.test('03-01-1994 12:30 PM'), True)
        self.assertEqual(datetime_type.test(datetime.datetime(1994, 3, 1, 12, 30)), True)

    def test_iso_format(self):
        values = ('1994-03-01T12:30:00', '2011-02-17T06:30')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0),
            datetime.datetime(2011, 2, 17, 6, 30, 0)
        ))

    def test_cast_parser(self):
        values = ('3/1/1994 12:30 PM', '2/17/2011 06:30', None, 'January 5th, 1984 22:37', 'n/a', '2015-01-01 02:34')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0),
            datetime.datetime(2011, 2, 17, 6, 30, 0),
            None,
            datetime.datetime(1984, 1, 5, 22, 37, 0),
            None,
            datetime.datetime(2015, 1, 1, 2, 34, 0)
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

    def test_cast_error(self):
        with self.assertRaises(CastError):
            self.type.cast('quack')

    def test_pickle_parser(self):
        from_pickle = pickle.loads(pickle.dumps(self.type))
        self.assertEqual(from_pickle.datetime_format, self.type.datetime_format)
        self.assertEqual(from_pickle.timezone, self.type.timezone)
        self.assertEqual(from_pickle._source_time, self.type._source_time)
        self.assertIsInstance(from_pickle._parser, parsedatetime.Calendar)


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
        self.assertEqual(self.type.test('2015-01-01 02:34'), False)
        self.assertEqual(self.type.test(datetime.datetime(1994, 3, 1, 12, 30)), False)
        self.assertEqual(self.type.test('4:10'), True)
        self.assertEqual(self.type.test(datetime.timedelta(hours=4, minutes=10)), True)
        self.assertEqual(self.type.test('a'), False)
        self.assertEqual(self.type.test('A\nB'), False)
        self.assertEqual(self.type.test(u'👍'), False)
        self.assertEqual(self.type.test('05_leslie3d_base'), False)
        self.assertEqual(self.type.test('2016-12-29'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30Z'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30+06:00'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30-06:00'), False)

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
