#!/usr/bin/env python

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

import shutil

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate import Table, TableSet
from agate.aggregations import *
from agate.column_types import TextType, NumberType
from agate.computations import Formula
from agate.exceptions import ColumnDoesNotExistError

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

        self.text_type = TextType()
        self.number_type = NumberType()

        self.columns = (
            ('letter', self.text_type),
            ('number', self.number_type)
        )

        self.tables = OrderedDict([
            ('table1', Table(self.table1, self.columns)),
            ('table2', Table(self.table2, self.columns)),
            ('table3', Table(self.table3, self.columns))
        ])

    def test_create_tableset(self):
        tableset = TableSet(self.tables)

        self.assertEqual(len(tableset), 3)

    def test_from_csv(self):
        tableset1 = TableSet(self.tables)
        tableset2 = TableSet.from_csv('examples/tableset', self.columns)

        self.assertSequenceEqual(tableset1.get_column_names(), tableset2.get_column_names())
        self.assertSequenceEqual(tableset1.get_column_types(), tableset2.get_column_types())

        self.assertEqual(len(tableset1), len(tableset2))

        for name in ['table1', 'table2', 'table3']:
            self.assertEqual(len(tableset1[name].columns), len(tableset2[name].columns))
            self.assertEqual(len(tableset1[name].rows), len(tableset2[name].rows))

            self.assertSequenceEqual(tableset1[name].rows[0], tableset2[name].rows[0])
            self.assertSequenceEqual(tableset1[name].rows[1], tableset2[name].rows[1])
            self.assertSequenceEqual(tableset1[name].rows[2], tableset2[name].rows[2])

    def test_to_csv(self):
        tableset = TableSet(self.tables)

        tableset.to_csv('.test-tableset')

        for name in ['table1', 'table2', 'table3']:
            with open('.test-tableset/%s.csv' % name) as f:
                contents1 = f.read()

            with open('examples/tableset/%s.csv' % name) as f:
                contents2 = f.read()

            self.assertEqual(contents1, contents2)

        shutil.rmtree('.test-tableset')

    def test_get_column_types(self):
        tableset = TableSet(self.tables)

        self.assertSequenceEqual(tableset.get_column_types(), [t for n, t in self.columns])

    def test_get_column_names(self):
        tableset = TableSet(self.tables)

        self.assertSequenceEqual(tableset.get_column_names(), [n for n, t in self.columns])

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
            ('number', Sum(), 'number_sum')
        ])

        self.assertIsInstance(new_table, Table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)
        self.assertSequenceEqual(new_table._column_names, ('group', 'count', 'number_sum'))
        self.assertSequenceEqual(new_table.rows[0], ('table1', 3, 6))
        self.assertSequenceEqual(new_table.rows[1], ('table2', 3, 7))
        self.assertSequenceEqual(new_table.rows[2], ('table3', 3, 6))

    def test_aggregate_min(self):
        tableset = TableSet(self.tables)

        new_table = tableset.aggregate([
            ('number', Min(), 'number_min')
        ])

        self.assertIsInstance(new_table, Table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)
        self.assertSequenceEqual(new_table._column_names, ('group', 'count', 'number_min'))
        self.assertIsInstance(new_table.columns['number_min'], NumberColumn)
        self.assertSequenceEqual(new_table.rows[0], ('table1', 3, 1))
        self.assertSequenceEqual(new_table.rows[1], ('table2', 3, 0))
        self.assertSequenceEqual(new_table.rows[2], ('table3', 3, 1))

    def test_aggregate_two_ops(self):
        tableset = TableSet(self.tables)

        new_table = tableset.aggregate([
            ('number', Sum(), 'number_sum'),
            ('number', Mean(), 'number_mean')
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
            ('letter', MaxLength(), 'letter_max_length')
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

        with self.assertRaises(UnsupportedAggregationError):
            tableset.aggregate([('letter', Sum(), 'letter_sum')])

    def test_aggregeate_bad_column(self):
        tableset = TableSet(self.tables)

        with self.assertRaises(ColumnDoesNotExistError):
            tableset.aggregate([('one', Sum(), 'one_sum')])

        with self.assertRaises(ColumnDoesNotExistError):
            tableset.aggregate([('bad', Sum(), 'bad_sum')])
