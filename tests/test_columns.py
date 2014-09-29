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

from journalism import Table
from journalism.columns import TextType, BooleanType, NumberType, DateType, DateTimeType, TextColumn, BooleanColumn, NumberColumn, DateColumn, DateTimeColumn
from journalism.exceptions import CastError, ColumnDoesNotExistError, NullComputationError

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

class TestColumns(unittest.TestCase):
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

    def test_stringify(self):
        self.assertEqual(str(self.table.columns['one']), "<journalism.columns.NumberColumn: (1, 2, None)>")

    def test_stringify_long(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )
        
        self.table = Table(rows, self.column_types, self.column_names)

        self.assertEqual(str(self.table.columns['one']), "<journalism.columns.NumberColumn: (1, 2, None, 1, 2, ...)>")

    def test_length(self):
        self.assertEqual(len(self.table.columns), 3)

    def test_get_column_data(self):
        self.assertSequenceEqual(self.table.columns['one']._data(), (1, 2, None))

    def test_get_column_data_cached(self):
        c = self.table.columns['one']

        self.assertIs(c._cached_data, None)

        data = c._data()

        self.assertSequenceEqual(c._cached_data, (1, 2, None))
        
        data2 = c._data()

        self.assertIs(data, data2)

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

    def test_any(self):
        self.assertEqual(self.table.columns['one'].any(lambda d: d == 2), True)
        self.assertEqual(self.table.columns['one'].any(lambda d: d == 5), False)

    def test_all(self):
        self.assertEqual(self.table.columns['one'].all(lambda d: d != 5), True)
        self.assertEqual(self.table.columns['one'].all(lambda d: d == 2), False)

    def test_count(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.column_types, self.column_names)

        self.assertEqual(table.columns['one'].count(1), 3)
        self.assertEqual(table.columns['one'].count(4), 0)
        self.assertEqual(table.columns['one'].count(None), 1)

    def test_counts(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.column_types, self.column_names)

        counts = table.columns['one'].counts()

        self.assertEqual(len(counts), 3)

        self.assertEqual(counts[1], 3)
        self.assertEqual(counts[2], 1)
        self.assertEqual(counts[None], 1)

    def test_percentile(self):
        rows = [(n,) for n in range(0, 101)]

        table = Table(rows, (self.number_type,), ('ints',))

        self.assertEqual(table.columns['ints'].percentile(25), Decimal(25))
        self.assertEqual(table.columns['ints'].percentile(50), Decimal(50))
        self.assertEqual(table.columns['ints'].percentile(75), Decimal(75))
        self.assertEqual(table.columns['ints'].percentile(100), Decimal(100))

    def test_percentile_range(self):
        rows = [(n,) for n in range(0, 101)]

        table = Table(rows, (self.number_type,), ('ints',))

        self.assertEqual(table.columns['ints'].percentile()[24], Decimal(25))
        self.assertEqual(table.columns['ints'].percentile()[49], Decimal(50))
        self.assertEqual(table.columns['ints'].percentile()[74], Decimal(75))
        self.assertEqual(table.columns['ints'].percentile()[99], Decimal(100))

    def test_percentile_not_valid(self):
        rows = [(n,) for n in range(0, 101)]

        table = Table(rows, (self.number_type,), ('ints',))

        with self.assertRaises(ValueError):
            table.columns['ints'].percentile(1.1)

        with self.assertRaises(ValueError):
            table.columns['ints'].percentile(103)

    def test_percentile_no_data(self):
        rows = (())

        table = Table(rows, (self.number_type,), ('ints',))

        self.assertEqual(table.columns['ints'].percentile(7), None)

class TestTextColumn(unittest.TestCase):
    def test_max_length(self):
        column = TextColumn(None, 'one')
        column._data = lambda: ('a', 'gobble', 'wow')
        self.assertEqual(column.max_length(), 6)

class TestBooleanColumn(unittest.TestCase):
    def test_any(self):
        column = BooleanColumn(None, 'one')
        column._data = lambda: (True, False, None)
        self.assertEqual(column.any(), True)

        column._data = lambda: (False, False, None)
        self.assertEqual(column.any(), False)

    def test_all(self):
        column = BooleanColumn(None, 'one')
        column._data = lambda: (True, True, None)
        self.assertEqual(column.all(), False)

        column._data = lambda: (True, True, True)
        self.assertEqual(column.all(), True)

class TestNumberColumn(unittest.TestCase):
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
        self.assertEqual(self.table.columns['one'].sum(), Decimal('6.5'))
        self.assertEqual(self.table.columns['two'].sum(), Decimal('13.13'))

    def test_min(self):
        self.assertEqual(self.table.columns['one'].min(), Decimal('1.1'))
        self.assertEqual(self.table.columns['two'].min(), Decimal('2.19'))

    def test_max(self):
        self.assertEqual(self.table.columns['one'].max(), Decimal('2.7'))
        self.assertEqual(self.table.columns['two'].max(), Decimal('4.1'))

    def test_median(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].median()

        self.assertEqual(self.table.columns['two'].median(), Decimal('3.42'))

    def test_mode(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].mode()

        self.assertEqual(self.table.columns['two'].mode(), Decimal('3.42'))

    def test_variance(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].variance()
        
        self.assertEqual(self.table.columns['two'].variance().quantize(Decimal('0.01')), Decimal('0.47'))

    def test_stdev(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].stdev()

        self.assertAlmostEqual(self.table.columns['two'].stdev().quantize(Decimal('0.01')), Decimal('0.69'))

    def test_mad(self):
        with self.assertRaises(NullComputationError):
            self.table.columns['one'].mad()

        self.assertAlmostEqual(self.table.columns['two'].mad(), Decimal('0'))

    def test_benfords_law(self):
        self.rows = (
            (Decimal('1.1'), Decimal('2.19'), 'a'),
            (Decimal('2.7'), Decimal('3.42'), 'b'),
            (None, Decimal('4.1'), 'c'),
            (Decimal('2.7'), Decimal('3.42'), 'c'),
            (Decimal('2.7'), Decimal('-2.42'), 'd')
        )
        self.table = Table(self.rows, self.column_types, self.column_names)

        with self.assertRaises(NullComputationError):
            self.table.columns['one'].benfords_law()

        self.assertAlmostEqual(self.table.columns['two'].benfords_law().quantize(Decimal('0.001')), Decimal('0.164'))
        self.assertAlmostEqual(self.table.columns['two'].benfords_law('negative').quantize(Decimal('0.001')), Decimal('0.296'))
        self.assertAlmostEqual(self.table.columns['two'].benfords_law('both').quantize(Decimal('0.001')), Decimal('0.247'))

class TestDateColumn(unittest.TestCase):
    def test_min(self):
        column = DateColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            datetime.date(1984, 1, 5)
        )

        self.assertEqual(column.min(), datetime.date(1011, 2, 17)) 

    def test_max(self):
        column = DateColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            datetime.date(1984, 1, 5)
        )

        self.assertEqual(column.max(), datetime.date(1994, 3, 1)) 

class TestDateTimeColumn(unittest.TestCase):
    def test_min(self):
        column = DateTimeColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.datetime(1994, 3, 3, 6, 31),
            datetime.datetime(1994, 3, 3, 6, 30, 30),
            datetime.datetime(1994, 3, 3, 6, 30)
        )

        self.assertEqual(column.min(), datetime.datetime(1994, 3, 3, 6, 30)) 

    def test_max(self):
        column = DateTimeColumn(None, 'one')
        column._data_without_nulls = lambda: (
            datetime.datetime(1994, 3, 3, 6, 31),
            datetime.datetime(1994, 3, 3, 6, 30, 30),
            datetime.datetime(1994, 3, 3, 6, 30)
        )

        self.assertEqual(column.max(), datetime.datetime(1994, 3, 3, 6, 31)) 

