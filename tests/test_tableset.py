#!/usr/bin/env python

from collections import OrderedDict

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import shutil
import json

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate import Table, TableSet
from agate.aggregations import *
from agate.data_types import *
from agate.computations import Formula
from agate.testcase import AgateTestCase

class TestTableSet(AgateTestCase):
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

        self.column_names = ['letter', 'number']
        self.column_types = [self.text_type, self.number_type]

        self.tables = OrderedDict([
            ('table1', Table(self.table1, self.column_names, self.column_types)),
            ('table2', Table(self.table2, self.column_names, self.column_types)),
            ('table3', Table(self.table3, self.column_names, self.column_types))
        ])

    def test_create_tableset(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        self.assertEqual(len(tableset), 3)

    def test_create_tableset_mismatched_column_names(self):
        tables = OrderedDict([
            ('table1', Table(self.table1, self.column_names, self.column_types)),
            ('table2', Table(self.table2, self.column_names, self.column_types)),
            ('table3', Table(self.table3, ['foo', 'bar'], self.column_types))
        ])

        with self.assertRaises(ValueError):
            tableset = TableSet(tables.values(), tables.keys())

    def test_create_tableset_mismatched_column_types(self):
        tables = OrderedDict([
            ('table1', Table(self.table1, self.column_names, self.column_types)),
            ('table2', Table(self.table2, self.column_names, self.column_types)),
            ('table3', Table(self.table3, self.column_names, [self.text_type, self.text_type]))
        ])

        with self.assertRaises(ValueError):
            tableset = TableSet(tables.values(), tables.keys())

    def test_from_csv(self):
        tableset1 = TableSet(self.tables.values(), self.tables.keys())
        tableset2 = TableSet.from_csv('examples/tableset', self.column_names, self.column_types)

        self.assertSequenceEqual(tableset1.column_names, tableset2.column_names)
        self.assertSequenceEqual(tableset1.column_types, tableset2.column_types)

        self.assertEqual(len(tableset1), len(tableset2))

        for name in ['table1', 'table2', 'table3']:
            self.assertEqual(len(tableset1[name].columns), len(tableset2[name].columns))
            self.assertEqual(len(tableset1[name].rows), len(tableset2[name].rows))

            self.assertSequenceEqual(tableset1[name].rows[0], tableset2[name].rows[0])
            self.assertSequenceEqual(tableset1[name].rows[1], tableset2[name].rows[1])
            self.assertSequenceEqual(tableset1[name].rows[2], tableset2[name].rows[2])

    def test_tableset_from_csv_invalid_dir(self):
        with self.assertRaises(IOError):
            TableSet.from_csv('quack')

    def test_to_csv(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        tableset.to_csv('.test-tableset')

        for name in ['table1', 'table2', 'table3']:
            with open('.test-tableset/%s.csv' % name) as f:
                contents1 = f.read()

            with open('examples/tableset/%s.csv' % name) as f:
                contents2 = f.read()

            self.assertEqual(contents1, contents2)

        shutil.rmtree('.test-tableset')

    def test_to_json(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        tableset.to_json('.test-tableset')

        for name in ['table1', 'table2', 'table3']:
            with open('.test-tableset/%s.json' % name) as f:
                contents1 = json.load(f)

            with open('examples/tableset/%s.json' % name) as f:
                contents2 = json.load(f)

            self.assertEqual(contents1, contents2)

        shutil.rmtree('.test-tableset')
    
    def test_to_nested_json(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())
        
        output = StringIO()
        tableset.to_json(output, nested=True)
        tableset.to_json('.test-tableset/tableset.json', nested=True)

        contents1 = json.loads(output.getvalue())
        
        with open('.test-tableset/tableset.json') as f:
            contents2 = json.load(f)

        with open('examples/tableset/tableset.json') as f:
            contents3 = json.load(f)

        self.assertEqual(contents1, contents3)
        self.assertEqual(contents2, contents3)

        shutil.rmtree('.test-tableset')

    def test_get_column_types(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        self.assertSequenceEqual(tableset.column_types, self.column_types)

    def test_get_column_names(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        self.assertSequenceEqual(tableset.column_names, self.column_names)

    def test_merge(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        table = tableset.merge()

        self.assertColumnNames(table, ['group', 'letter', 'number'])
        self.assertColumnTypes(table, [Text, Text, Number])

        self.assertEqual(len(table.rows), 9)
        self.assertSequenceEqual(table.rows[0], ['table1', 'a', 1])
        self.assertSequenceEqual(table.rows[8], ['table3', 'c', 3])

    def test_merge_key_name(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='foo')

        table = tableset.merge()

        self.assertColumnNames(table, ['foo', 'letter', 'number'])
        self.assertColumnTypes(table, [Text, Text, Number])
    
    def test_merge_groups(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='foo')

        table = tableset.merge(groups=['red', 'blue', 'green'], group_name='color_code')

        self.assertColumnNames(table, ['color_code', 'letter', 'number'])
        self.assertColumnTypes(table, [Text, Text, Number])
        
        self.assertEqual(len(table.rows), 9)
        self.assertSequenceEqual(table.rows[0], ['red', 'a', 1])
        self.assertSequenceEqual(table.rows[8], ['green', 'c', 3])
    
    def test_merge_groups_invalid_length(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        with self.assertRaises(ValueError):
            table = tableset.merge(groups=['red', 'blue'], group_name='color_code')
    
    def test_merge_groups_invalid_type(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        with self.assertRaises(ValueError):
            table = tableset.merge(groups='invalid', group_name='color_code')

    def test_compute(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_tableset = tableset.compute([
            ('new_column', Formula(self.text_type, lambda r: '%(letter)s-%(number)i' % r))
        ])

        new_table = new_tableset['table1']

        self.assertColumnNames(new_table, ('letter', 'number', 'new_column',))
        self.assertColumnTypes(new_table, (Text, Number, Text))
        self.assertRows(new_table, [
            ('a', 1, 'a-1'),
            ('a', 3, 'a-3'),
            ('b', 2, 'b-2')
        ])

        new_table = new_tableset['table2']

        self.assertRows(new_table, [
            ('b', 0, 'b-0'),
            ('a', 2, 'a-2'),
            ('c', 5, 'c-5')
        ])

        new_table = new_tableset['table3']

        self.assertSequenceEqual(new_table.rows[0], ('a', 1, 'a-1'))
        self.assertSequenceEqual(new_table.rows[1], ('a', 2, 'a-2'))
        self.assertSequenceEqual(new_table.rows[2], ('c', 3, 'c-3'))

    def test_select(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_tableset = tableset.select(['number'])

        for name, new_table in new_tableset.items():
            self.assertColumnNames(new_table, ('number',))
            self.assertColumnTypes(new_table, (Number,))

    def test_aggregate_key_name(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        new_table = tableset.aggregate([
            ('count', Length())
        ])

        self.assertIsInstance(new_table, Table)
        self.assertColumnNames(new_table, ('test', 'count'))
        self.assertColumnTypes(new_table, [Text, Number])

    def test_aggregate_key_type(self):
        tables = OrderedDict([
            (1, Table(self.table1, self.column_names, self.column_types)),
            (2, Table(self.table2, self.column_names, self.column_types)),
            (3, Table(self.table3, self.column_names, self.column_types))
        ])

        tableset = TableSet(tables.values(), tables.keys(), key_name='test', key_type=self.number_type)

        new_table = tableset.aggregate([
            ('count', Length())
        ])

        self.assertIsInstance(new_table, Table)
        self.assertColumnNames(new_table, ('test', 'count'))
        self.assertColumnTypes(new_table, [Number, Number])

    def test_aggregate_row_names(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        new_table = tableset.aggregate([
            ('count', Length())
        ])

        self.assertRowNames(new_table, ['table1', 'table2', 'table3'])

    def test_aggregate_sum(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_table = tableset.aggregate([
            ('count', Length()),
            ('number_sum', Sum('number'))
        ])

        self.assertIsInstance(new_table, Table)
        self.assertColumnNames(new_table, ('group', 'count', 'number_sum'))
        self.assertColumnTypes(new_table, [Text, Number, Number])
        self.assertRows(new_table, [
            ('table1', 3, 6),
            ('table2', 3, 7),
            ('table3', 3, 6)
        ])


    def test_aggregate_min(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_table = tableset.aggregate([
            ('count', Length()),
            ('number_min', Min('number'))
        ])

        self.assertIsInstance(new_table, Table)
        self.assertColumnNames(new_table, ('group', 'count', 'number_min'))
        self.assertColumnTypes(new_table, [Text, Number, Number])
        self.assertRows(new_table, [
            ('table1', 3, 1),
            ('table2', 3, 0),
            ('table3', 3, 1)
        ])

    def test_aggregate_two_ops(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_table = tableset.aggregate([
            ('count', Length()),
            ('number_sum', Sum('number')),
            ('number_mean', Mean('number'))
        ])

        self.assertIsInstance(new_table, Table)
        self.assertColumnNames(new_table, ('group', 'count', 'number_sum', 'number_mean'))
        self.assertColumnTypes(new_table, [Text, Number, Number, Number])
        self.assertRows(new_table, [
            ('table1', 3, 6, 2),
            ('table2', 3, 7, Decimal(7) / 3),
            ('table3', 3, 6, 2)
        ])

    def test_aggregate_max_length(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_table = tableset.aggregate([
            ('count', Length()),
            ('letter_max_length', MaxLength('letter'))
        ])

        self.assertIsInstance(new_table, Table)
        self.assertColumnNames(new_table, ('group', 'count', 'letter_max_length'))
        self.assertColumnTypes(new_table, [Text, Number, Number])
        self.assertRows(new_table, [
            ('table1', 3, 1),
            ('table2', 3, 1),
            ('table3', 3, 1)
        ])

    def test_aggregate_sum_invalid(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        with self.assertRaises(DataTypeError):
            tableset.aggregate([('letter_sum', Sum('letter'))])

    def test_aggregeate_bad_column(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        with self.assertRaises(KeyError):
            tableset.aggregate([('one_sum', Sum('one'))])

        with self.assertRaises(KeyError):
            tableset.aggregate([('bad_sum', Sum('bad'))])

    def test_nested(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

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
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        nested = tableset.group_by('letter')

        results = nested.aggregate([
            ('count', Length()),
            ('number_sum', Sum('number'))
        ])

        self.assertIsInstance(results, Table)
        self.assertColumnNames(results, ('test', 'letter', 'count', 'number_sum'))
        self.assertColumnTypes(results, (Text, Text, Number, Number))
        self.assertRows(results, [
            ('table1', 'a', 2, 4),
            ('table1', 'b', 1, 2),
            ('table2', 'b', 1, 0),
            ('table2', 'a', 1, 2),
            ('table2', 'c', 1, 5),
            ('table3', 'a', 2, 3),
            ('table3', 'c', 1, 3)
        ])

    def test_nested_aggregate_row_names(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        nested = tableset.group_by('letter')

        results = nested.aggregate([
            ('count', Length()),
            ('number_sum', Sum('number'))
        ])

        self.assertRowNames(results, [
            ('table1', 'a'),
            ('table1', 'b'),
            ('table2', 'b'),
            ('table2', 'a'),
            ('table2', 'c'),
            ('table3', 'a'),
            ('table3', 'c'),
        ])
        self.assertSequenceEqual(results.rows[('table1', 'a')], ('table1', 'a', 2, 4))
        self.assertSequenceEqual(results.rows[('table2', 'c')], ('table2', 'c', 1, 5))

    def test_proxy_local(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='foo')

        self.assertEqual(tableset._key_name, 'foo')

    def test_proxy_maintains_key(self):
        number_type = Number()

        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='foo', key_type=number_type)

        self.assertEqual(tableset.key_name, 'foo')
        self.assertEqual(tableset.key_type, number_type)

        new_tableset = tableset.select(['number'])

        self.assertEqual(new_tableset.key_name, 'foo')
        self.assertEqual(new_tableset.key_type, number_type)

    def test_proxy_invalid(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        with self.assertRaises(AttributeError):
            tableset.foo()
