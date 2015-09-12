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
from agate.data_types import *
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

        self.text_type = Text()
        self.number_type = Number()

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

    def test_aggregate_key_name(self):
        tableset = TableSet(self.tables, key_name='test')

        new_table = tableset.aggregate([
            ('number', Length(), 'count')
        ])

        self.assertIsInstance(new_table, Table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 2)
        self.assertSequenceEqual(new_table._column_names, ('test', 'count'))
        self.assertIsInstance(new_table._column_types[0], Text)
        self.assertIsInstance(new_table._column_types[1], Number)

    def test_aggregate_key_type(self):
        tables = OrderedDict([
            (1, Table(self.table1, self.columns)),
            (2, Table(self.table2, self.columns)),
            (3, Table(self.table3, self.columns))
        ])

        tableset = TableSet(tables, key_name='test', key_type=self.number_type)

        new_table = tableset.aggregate([
            ('number', Length(), 'count')
        ])

        self.assertIsInstance(new_table, Table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 2)
        self.assertSequenceEqual(new_table._column_names, ('test', 'count'))
        self.assertIsInstance(new_table._column_types[0], Number)
        self.assertIsInstance(new_table._column_types[1], Number)

    def test_aggregate_sum(self):
        tableset = TableSet(self.tables)

        new_table = tableset.aggregate([
            ('number', Length(), 'count'),
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
            ('number', Length(), 'count'),
            ('number', Min(), 'number_min')
        ])

        self.assertIsInstance(new_table, Table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)
        self.assertSequenceEqual(new_table._column_names, ('group', 'count', 'number_min'))
        self.assertIsInstance(new_table.columns['number_min'].data_type, Number)
        self.assertSequenceEqual(new_table.rows[0], ('table1', 3, 1))
        self.assertSequenceEqual(new_table.rows[1], ('table2', 3, 0))
        self.assertSequenceEqual(new_table.rows[2], ('table3', 3, 1))

    def test_aggregate_two_ops(self):
        tableset = TableSet(self.tables)

        new_table = tableset.aggregate([
            ('number', Length(), 'count'),
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
            ('letter', Length(), 'count'),
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

        with self.assertRaises(DataTypeError):
            tableset.aggregate([('letter', Sum(), 'letter_sum')])

    def test_aggregeate_bad_column(self):
        tableset = TableSet(self.tables)

        with self.assertRaises(ColumnDoesNotExistError):
            tableset.aggregate([('one', Sum(), 'one_sum')])

        with self.assertRaises(ColumnDoesNotExistError):
            tableset.aggregate([('bad', Sum(), 'bad_sum')])

    def test_nested(self):
        tableset = TableSet(self.tables, key_name='test')

        nested = tableset.group_by('letter')

        self.assertIsInstance(nested, TableSet)
        self.assertEqual(len(nested), 3)
        self.assertSequenceEqual(nested._column_names, ('letter', 'number'))
        self.assertSequenceEqual(nested._column_types, (self.text_type, self.number_type))

        self.assertIsInstance(nested['table1'], TableSet)
        self.assertEqual(len(nested['table1']), 2)
        self.assertSequenceEqual(nested['table1']._column_names, ('letter', 'number'))
        self.assertSequenceEqual(nested['table1']._column_types, (self.text_type, self.number_type))

        self.assertIsInstance(nested['table1']['a'], Table)
        self.assertEqual(len(nested['table1']['a'].columns), 2)
        self.assertEqual(len(nested['table1']['a'].rows), 2)

    def test_nested_aggregation(self):
        tableset = TableSet(self.tables, key_name='test')

        nested = tableset.group_by('letter')

        results = nested.aggregate([
            ('letter', Length(), 'count'),
            ('number', Sum(), 'number_sum')
        ])

        self.assertIsInstance(results, Table)
        self.assertEqual(len(results.rows), 7)
        self.assertEqual(len(results.columns), 4)
        self.assertSequenceEqual(results._column_names, ('test', 'letter', 'count', 'number_sum'))

        self.assertSequenceEqual(results.rows[0], ('table1', 'a', 2, 4))
        self.assertSequenceEqual(results.rows[1], ('table1', 'b', 1, 2))

        self.assertSequenceEqual(results.rows[2], ('table2', 'b', 1, 0))
        self.assertSequenceEqual(results.rows[3], ('table2', 'a', 1, 2))
        self.assertSequenceEqual(results.rows[4], ('table2', 'c', 1, 5))

        self.assertSequenceEqual(results.rows[5], ('table3', 'a', 2, 3))
        self.assertSequenceEqual(results.rows[6], ('table3', 'c', 1, 3))
