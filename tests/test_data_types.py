import datetime
import pickle
import unittest
from decimal import Decimal

import parsedatetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for Python < 3.9
    from backports.zoneinfo import ZoneInfo

from agate.data_types import Boolean, Date, DateTime, Number, Text, TimeDelta
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
        self.assertEqual(self.type.test('👍'), True)
        self.assertEqual(self.type.test('05_leslie3d_base'), True)
        self.assertEqual(self.type.test('2016-12-29'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30Z'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30+06:00'), True)
        self.assertEqual(self.type.test('2016-12-29T11:43:30-06:00'), True)

    def test_cast(self):
        values = ('a', 1, None, Decimal('2.7'), 'n/a', '👍', ' foo', 'foo ')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, ('a', '1', None, '2.7', None, '👍', ' foo', 'foo '))

    def test_no_cast_nulls(self):
        values = ('', 'N/A', None)

        t = Text()
        casted = tuple(t.cast(v) for v in values)
        self.assertSequenceEqual(casted, (None, None, None))

        t = Text(cast_nulls=False)
        casted = tuple(t.cast(v) for v in values)
        self.assertSequenceEqual(casted, ('', 'N/A', None))

    def test_null_values(self):
        t = Text(null_values=['Bad Value'])
        self.assertEqual(t.cast('Bad Value'), None)


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
        self.assertEqual(self.type.test('👍'), False)
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
        self.assertEqual(self.type.test(True), True)
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
        self.assertEqual(self.type.test('👍'), False)
        self.assertEqual(self.type.test('05_leslie3d_base'), False)
        self.assertEqual(self.type.test('2016-12-29'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30Z'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30+06:00'), False)
        self.assertEqual(self.type.test('2016-12-29T11:43:30-06:00'), False)

    def test_cast(self):
        values = (2, 1, None, Decimal('2.7'), 'n/a', '2.7', '200,000,000')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(
            casted,
            (Decimal('2'), Decimal('1'), None, Decimal('2.7'), None, Decimal('2.7'), Decimal('200000000'))
        )

    def test_boolean_cast(self):
        values = (True, False)
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (Decimal('1'), Decimal('0')))

    def test_currency_cast(self):
        values = ('$2.70', '-$0.70', '€14', '50¢', '-75¢', '-$1,287')
        casted = tuple(self.type.cast(v) for v in values)
        self.assertSequenceEqual(
            casted,
            (Decimal('2.7'), Decimal('-0.7'), Decimal('14'), Decimal('50'), Decimal('-75'), Decimal('-1287'))
        )

    def test_cast_locale(self):
        values = (2, 1, None, Decimal('2.7'), 'n/a', '2,7', '200.000.000')
        casted = tuple(Number(locale='de_DE.UTF-8').cast(v) for v in values)
        self.assertSequenceEqual(
            casted,
            (Decimal('2'), Decimal('1'), None, Decimal('2.7'), None, Decimal('2.7'), Decimal('200000000'))
        )

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
        self.assertEqual(self.type.test('👍'), False)
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

    def test_cast_format_locale(self):
        date_type = Date(date_format='%d-%b-%Y', locale='de_DE.UTF-8')

        # March can be abbreviated to Mrz or Mär depending on the locale version,
        # so we use December in the first value to ensure the test passes everywhere.
        # NetBSD has a different locale database than glibc.
        try:
            values = ('01-Dez-1994', '17-Feb-2011', None, '05-Jan-1984', 'n/a')
            casted = tuple(date_type.cast(v) for v in values)
        except CastError:
            values = ('01-Dez.-1994', '17-Feb.-2011', None, '05-Jan.-1984', 'n/a')
            casted = tuple(date_type.cast(v) for v in values)

        self.assertSequenceEqual(casted, (
            datetime.date(1994, 12, 1),
            datetime.date(2011, 2, 17),
            None,
            datetime.date(1984, 1, 5),
            None
        ))

    def test_cast_locale(self):
        date_type = Date(locale='fr_FR')

        values = ('01 mars 1994', 'jeudi 17 février 2011', None, '5 janvier 1984', 'n/a')
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
        self.assertEqual(from_pickle.locale, self.type.locale)
        self.assertIsInstance(from_pickle._constants, parsedatetime.Constants)
        self.assertIsInstance(from_pickle._parser, parsedatetime.Calendar)


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
        self.assertEqual(self.type.test('👍'), False)
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
        tzinfo = ZoneInfo('US/Pacific')
        datetime_type = DateTime(timezone=tzinfo)

        values = ('3/1/1994 12:30 PM', '2/17/2011 06:30', None, 'January 5th, 1984 22:37', 'n/a')
        casted = tuple(datetime_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0, 0, tzinfo=tzinfo),
            datetime.datetime(2011, 2, 17, 6, 30, 0, 0, tzinfo=tzinfo),
            None,
            datetime.datetime(1984, 1, 5, 22, 37, 0, 0, tzinfo=tzinfo),
            None
        ))

    def test_cast_format(self):
        datetime_type = DateTime(datetime_format='%m-%d-%Y %I:%M %p')

        values = ('03-01-1994 12:30 PM', '02-17-2011 06:30 AM', None, '01-05-1984 06:30 PM', 'n/a')
        casted = tuple(datetime_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0),
            datetime.datetime(2011, 2, 17, 6, 30, 0),
            None,
            datetime.datetime(1984, 1, 5, 18, 30, 0),
            None
        ))

    def test_cast_format_locale(self):
        date_type = DateTime(datetime_format='%Y-%m-%d %I:%M %p', locale='ko_KR.UTF-8')

        # Date formats depend on the platform's strftime/strptime implementation;
        # some platforms like macOS always return AM/PM for day periods (%p),
        # so we will catch any CastError that may arise from the conversion
        possible_values = (
            ('1994-03-01 12:30 오후', '2011-02-17 06:30 오전', None, '1984-01-05 06:30 오후', 'n/a'),
            ('1994-03-01 12:30 PM', '2011-02-17 06:30 AM', None, '1984-01-05 06:30 PM', 'n/a'),
        )
        valid = False
        exceptions = []
        for values in possible_values:
            try:
                casted = tuple(date_type.cast(v) for v in values)
            except CastError as e:
                exceptions.append(repr(e))
                continue
            self.assertSequenceEqual(casted, (
                datetime.datetime(1994, 3, 1, 12, 30, 0),
                datetime.datetime(2011, 2, 17, 6, 30, 0),
                None,
                datetime.datetime(1984, 1, 5, 18, 30, 0),
                None
            ))
            valid = True
        if not valid:
            raise AssertionError('\n\n'.join(exceptions))

    def test_cast_locale(self):
        date_type = DateTime(locale='fr_FR')

        values = ('01/03/1994 12:30', '17/2/11 6:30', None, '5/01/84 18:30', 'n/a')
        casted = tuple(date_type.cast(v) for v in values)
        self.assertSequenceEqual(casted, (
            datetime.datetime(1994, 3, 1, 12, 30, 0),
            datetime.datetime(2011, 2, 17, 6, 30, 0),
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
        self.assertEqual(from_pickle.locale, self.type.locale)
        self.assertEqual(from_pickle._source_time, self.type._source_time)
        self.assertIsInstance(from_pickle._constants, parsedatetime.Constants)
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
        self.assertEqual(self.type.test('👍'), False)
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
