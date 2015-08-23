#!/usr/bin/env python

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from journalism import Table, TableSet
from journalism.columns import TextType, NumberType
from journalism.computers import Formula
from journalism.exceptions import ColumnDoesNotExistError, UnsupportedOperationError

class TestTableSet(unittest.TestCase):
    def setUp(self):
        self.table1 = (
            ('a', 1),
            ('a', 3),
            ('b', 2)
        )

        self.table2 = (
            ('b', 0),
            ('a', 2),
            ('c', 5)
        )

        self.table3 = (
            ('a', 1),
            ('a', 2),
            ('c', 3)
        )

        self.column_names = ('letter', 'number')
        self.text_type = TextType()
        self.number_type = NumberType()
        self.column_types = (self.text_type, self.number_type)

        self.tables = OrderedDict([
            ('table1', Table(self.table1, self.column_types, self.column_names)),
            ('table2', Table(self.table2, self.column_types, self.column_names)),
            ('table3', Table(self.table3, self.column_types, self.column_names))
        ])

    def test_create_tableset(self):
        tableset = TableSet(self.tables)

        self.assertEqual(len(tableset), 3)

    def test_get_column_types(self):
        tableset = TableSet(self.tables)

        self.assertEqual(tableset.get_column_types(), self.column_types)

    def test_get_column_names(self):
        tableset = TableSet(self.tables)

        self.assertSequenceEqual(tableset.get_column_names(), ('letter', 'number'))

    def test_select(self):
        tableset = TableSet(self.tables)

        new_tableset = tableset.compute([
            ('new_column', Formula(self.text_type, lambda r: '%(letter)s-%(number)i' % r))
        ])

        new_table = new_tableset['table1']

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)
        self.assertSequenceEqual(new_table._column_types, (self.text_type, self.number_type, self.text_type,))
        self.assertSequenceEqual(new_table._column_names, ('letter', 'number', 'new_column',))

        self.assertSequenceEqual(new_table.rows[0], ('a', 1, 'a-1'))
        self.assertSequenceEqual(new_table.rows[1], ('a', 3, 'a-3'))
        self.assertSequenceEqual(new_table.rows[2], ('b', 2, 'b-2'))

        new_table = new_tableset['table2']

        self.assertSequenceEqual(new_table.rows[0], ('b', 0, 'b-0'))
        self.assertSequenceEqual(new_table.rows[1], ('a', 2, 'a-2'))
        self.assertSequenceEqual(new_table.rows[2], ('c', 5, 'c-5'))

        new_table = new_tableset['table3']

        self.assertSequenceEqual(new_table.rows[0], ('a', 1, 'a-1'))
        self.assertSequenceEqual(new_table.rows[1], ('a', 2, 'a-2'))
        self.assertSequenceEqual(new_table.rows[2], ('c', 3, 'c-3'))

    def test_compute(self):
        tableset = TableSet(self.tables)

        new_tableset = tableset.select(['number'])

        for name, new_table in new_tableset.items():
            self.assertEqual(len(new_table.rows), 3)
            self.assertEqual(len(new_table.columns), 1)
            self.assertSequenceEqual(new_table._column_types, (self.number_type,))
            self.assertSequenceEqual(new_table._column_names, ('number',))

    def test_aggregate_sum(self):
        tableset = TableSet(self.tables)

        new_table = tableset.aggregate([
            ('number', 'sum')
        ])

        self.assertIsInstance(new_table, Table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)
        self.assertSequenceEqual(new_table._column_names, ('group', 'count', 'number_sum'))
        self.assertSequenceEqual(new_table.rows[0], ('table1', 3, 6))
        self.assertSequenceEqual(new_table.rows[1], ('table2', 3, 7))
        self.assertSequenceEqual(new_table.rows[2], ('table3', 3, 6))

    def test_aggregate_to_ops(self):
        tableset = TableSet(self.tables)

        new_table = tableset.aggregate([
            ('number', 'sum'),
            ('number', 'mean')
        ])

        self.assertIsInstance(new_table, Table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 4)
        self.assertSequenceEqual(new_table._column_names, ('group', 'count', 'number_sum', 'number_mean'))
        self.assertSequenceEqual(new_table.rows[0], ('table1', 3, 6, 2))
        self.assertSequenceEqual(new_table.rows[1], ('table2', 3, 7, Decimal(7) / 3))
        self.assertSequenceEqual(new_table.rows[2], ('table3', 3, 6, 2))

    def test_aggregate_max_length(self):
        tableset = TableSet(self.tables)

        new_table = tableset.aggregate([
            ('letter', 'max_length')
        ])

        self.assertIsInstance(new_table, Table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)
        self.assertSequenceEqual(new_table._column_names, ('group', 'count', 'letter_max_length'))
        self.assertSequenceEqual(new_table.rows[0], ('table1', 3, 1))
        self.assertSequenceEqual(new_table.rows[1], ('table2', 3, 1))
        self.assertSequenceEqual(new_table.rows[2], ('table3', 3, 1))

    def test_aggregate_sum_invalid(self):
        tableset = TableSet(self.tables)

        with self.assertRaises(UnsupportedOperationError):
            tableset.aggregate([('letter', 'sum')])

    def test_aggregeate_bad_column(self):
        tableset = TableSet(self.tables)

        with self.assertRaises(ColumnDoesNotExistError):
            tableset.aggregate([('one', 'sum')])

        with self.assertRaises(ColumnDoesNotExistError):
            tableset.aggregate([('bad', 'sum')])
