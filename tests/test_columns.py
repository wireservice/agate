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
from journalism.columns import TextType, BooleanType, NumberType, DateType, TextColumn, BooleanColumn, NumberColumn, DateColumn
from journalism.exceptions import CastError, ColumnDoesNotExistError, NullComputationError

class TestColumnTypes(unittest.TestCase):
    def test_text(self):
        self.assertIsInstance(TextType().create(None, 1), TextColumn)

    def test_boolean(self):
        self.assertIsInstance(BooleanType().create(None, 1), BooleanColumn)

    def test_number(self):
        self.assertIsInstance(NumberType().create(None, 1), NumberColumn)

    def test_date(self):
        self.assertIsInstance(DateType().create(None, 1), DateColumn)

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

        new_table = table.columns['one'].counts()

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.columns), 2)
        self.assertEqual(len(new_table.rows), 3) 

        self.assertSequenceEqual(new_table.rows[0], (1, 3))
        self.assertSequenceEqual(new_table.rows[1], (2, 1))
        self.assertSequenceEqual(new_table.rows[2], (None, 1))

        self.assertSequenceEqual(new_table.columns['one'], (1, 2, None))
        self.assertSequenceEqual(new_table.columns['count'], (3, 1, 1))

class TestTextColumn(unittest.TestCase):
    def test_cast(self):
        column = TextColumn(None, 'one')
        column._data = lambda: ('a', 1, None, Decimal('2.7'), 'n/a')
        self.assertSequenceEqual(column._cast(), ('a', '1', None, '2.7', None))

    def test_max_length(self):
        column = TextColumn(None, 'one')
        column._data = lambda: ('a', 'gobble', 'wow')
        self.assertEqual(column.max_length(), 6)

class TestBooleanColumn(unittest.TestCase):
    def test_cast(self):
        column = BooleanColumn(None, 'one')
        column._data = lambda: (True, 'yes', None, False, 'no', 'n/a')
        self.assertSequenceEqual(column._cast(), (True, True, None, False, False, None))

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

    def test_cast(self):
        column = NumberColumn(None, 'one')
        column._data = lambda: (2, 1, None, Decimal('2.7'), 'n/a')
        self.assertSequenceEqual(column._cast(), (Decimal('2'), Decimal('1'), None, Decimal('2.7'), None))

    def test_cast_text(self):
        column = NumberColumn(None, 'one')
        column._data = lambda: ('a', 1.1, None, Decimal('2.7'), 'n/a')

        with self.assertRaises(CastError):
            column._cast()

    def test_cast_float(self):
        column = NumberColumn(None, 'one')
        column._data = lambda: (2, 1.1, None, Decimal('2.7'), 'n/a')

        with self.assertRaises(CastError):
            column._cast()

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

class TestDateColumn(unittest.TestCase):
    def test_cast(self):
        column = DateColumn(None, 'one')
        column._data = lambda: ('3-1-1994', '2/17/1011', None, 'January 5th, 1984')
        self.assertSequenceEqual(column._cast(), (
            datetime.date(1994, 3, 1),
            datetime.date(1011, 2, 17),
            None,
            datetime.date(1984, 1, 5)
        ))

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

