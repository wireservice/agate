#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import os
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six
from six.moves import range

from agate import Table, TableSet
from agate.data_types import *
from agate.computations import Formula
from agate.exceptions import DataTypeError

class TestTable(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, u'👍')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

    def test_create_table(self):
        table = Table(self.rows, self.column_names, self.column_types)

        self.assertEqual(len(table.rows), 3)
        self.assertEqual(len(table.columns), 3)

        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[2], (None, 2, u'👍'))

    def test_create_table_non_string_columns(self):
        column_names = ['one', 'two', 3]

        with self.assertRaises(ValueError):
            Table(self.rows, column_names, self.column_types)

    def test_create_table_non_datatype_columns(self):
        column_types = [self.number_type, self.number_type, 'foo']

        with self.assertRaises(ValueError):
            Table(self.rows, self.column_names, column_types)

    def test_create_duplicate_column_names(self):
        column_names = ['one', 'two', 'two']

        with self.assertRaises(ValueError):
            Table(self.rows, column_names, self.column_types)

    def test_column_names_types_different_lengths(self):
        column_names = ['one', 'two', 'three', 'four']

        with self.assertRaises(ValueError):
            Table(self.rows, column_names, self.column_types)

    def test_create_variable_length_rows(self):
        rows = (
            (1, 4, 'a'),
            (2,),
            (None, 2)
        )

        table = Table(rows, self.column_names, self.column_types)

        self.assertEqual(len(table.rows), 3)
        self.assertEqual(len(table.columns), 3)

        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[1], (2, None, None))
        self.assertSequenceEqual(table.rows[2], (None, 2, None))

    def test_create_table_no_column_names(self):
        table = Table(self.rows, None, self.column_types)

        self.assertEqual(len(table.rows), 3)
        self.assertEqual(len(table.columns), 3)

        self.assertSequenceEqual(table.columns[0], (1, 2, None))
        self.assertSequenceEqual(table.columns['A'], (1, 2, None))

        with self.assertRaises(KeyError):
            table.columns[None]

        with self.assertRaises(KeyError):
            table.columns['one']

        self.assertSequenceEqual(table.columns[2], ('a', 'b', u'👍'))
        self.assertSequenceEqual(table.columns['C'], ('a', 'b', u'👍'))

        with self.assertRaises(KeyError):
            table.columns['']

    def test_row_too_long(self):
        rows = (
            (1, 4, 'a', 'foo'),
            (2,),
            (None, 2)
        )

        with self.assertRaises(ValueError):
            table = Table(rows, self.column_names, self.column_types)

    def test_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')

        self.assertSequenceEqual(table.row_names, [
            'a',
            'b',
            u'👍'
        ])
        self.assertSequenceEqual(table.rows['a'], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows['b'], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[u'👍'], (None, 2, u'👍'))

    def test_row_names_non_string(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='one')

        self.assertSequenceEqual(table.row_names, [
            Decimal('1'),
            Decimal('2'),
            None
        ])
        self.assertSequenceEqual(table.rows[Decimal('1')], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[Decimal('2')], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[None], (None, 2, u'👍'))

    def test_row_names_func(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names=lambda r: (r['one'], r['three']))

        self.assertSequenceEqual(table.row_names, [
            (Decimal('1'), 'a'),
            (Decimal('2'), 'b'),
            (None, u'👍')
        ])
        self.assertSequenceEqual(table.rows[(Decimal('1'), 'a')], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[(Decimal('2'), 'b')], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[(None, u'👍')], (None, 2, u'👍'))

    def test_from_csv(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test.csv', self.column_names, self.column_types)

        self.assertSequenceEqual(table1.column_names, table2.column_names)
        self.assertSequenceEqual(table1.column_types, table2.column_types)

        self.assertEqual(len(table1.columns), len(table2.columns))
        self.assertEqual(len(table1.rows), len(table2.rows))

        self.assertSequenceEqual(table1.rows[0], table2.rows[0])
        self.assertSequenceEqual(table1.rows[1], table2.rows[1])
        self.assertSequenceEqual(table1.rows[2], table2.rows[2])

    def test_from_csv_columns_and_header(self):
        column_names = ['a', 'b', 'c']

    def test_from_json(self):
        table = Table.from_json('examples/test.json')

        self.assertEqual(len(table.columns), 3)
        self.assertEqual(len(table.rows), 3)

        self.assertSequenceEqual(table.column_names, ['one', 'two', 'three'])
        self.assertIsInstance(table.columns[0].data_type, Number)
        self.assertIsInstance(table.columns[1].data_type, Number)
        self.assertIsInstance(table.columns[2].data_type, Text)

        self.assertSequenceEqual(table.rows[0], [1, 4, 'a'])
        self.assertSequenceEqual(table.rows[1], [2, 3, 'b'])
        self.assertSequenceEqual(table.rows[2], [None, 2, u'👍'])

    def test_from_json_file_like_object(self):
        with open('examples/test.json') as f:
            table = Table.from_json(f)

        self.assertEqual(len(table.columns), 3)
        self.assertEqual(len(table.rows), 3)

        self.assertSequenceEqual(table.column_names, ['one', 'two', 'three'])
        self.assertIsInstance(table.columns[0].data_type, Number)
        self.assertIsInstance(table.columns[1].data_type, Number)
        self.assertIsInstance(table.columns[2].data_type, Text)

        self.assertSequenceEqual(table.rows[0], [1, 4, 'a'])
        self.assertSequenceEqual(table.rows[1], [2, 3, 'b'])
        self.assertSequenceEqual(table.rows[2], [None, 2, u'👍'])

    def test_from_json_with_key(self):
        table = Table.from_json('examples/test_key.json', key='data')

        self.assertEqual(len(table.columns), 3)
        self.assertEqual(len(table.rows), 3)

        self.assertSequenceEqual(table.column_names, ['one', 'two', 'three'])
        self.assertIsInstance(table.columns[0].data_type, Number)
        self.assertIsInstance(table.columns[1].data_type, Number)
        self.assertIsInstance(table.columns[2].data_type, Text)

        self.assertSequenceEqual(table.rows[0], [1, 4, 'a'])
        self.assertSequenceEqual(table.rows[1], [2, 3, 'b'])
        self.assertSequenceEqual(table.rows[2], [None, 2, u'👍'])

    def test_from_json_mixed_keys(self):
        table = Table.from_json('examples/test_mixed.json')

        self.assertEqual(len(table.columns), 5)
        self.assertEqual(len(table.rows), 3)

        self.assertSequenceEqual(table.column_names, ['one', 'two', 'three', 'four', 'five'])
        self.assertIsInstance(table.columns[0].data_type, Number)
        self.assertIsInstance(table.columns[1].data_type, Number)
        self.assertIsInstance(table.columns[2].data_type, Text)
        self.assertIsInstance(table.columns[3].data_type, Text)
        self.assertIsInstance(table.columns[4].data_type, Number)

        self.assertSequenceEqual(table.rows[0], [1, 4, 'a', None, None])
        self.assertSequenceEqual(table.rows[1], [2, 3, 'b', 'd', None])
        self.assertSequenceEqual(table.rows[2], [None, 2, u'👍', None, 5])

    def test_from_json_nested(self):
        table = Table.from_json('examples/test_nested.json')

        self.assertEqual(len(table.columns), 6)
        self.assertEqual(len(table.rows), 2)

        self.assertSequenceEqual(table.column_names, ['one', 'two/two_a', 'two/two_b', 'three/0', 'three/1', 'three/2'])
        self.assertIsInstance(table.columns[0].data_type, Number)
        self.assertIsInstance(table.columns[1].data_type, Text)
        self.assertIsInstance(table.columns[2].data_type, Text)
        self.assertIsInstance(table.columns[3].data_type, Text)
        self.assertIsInstance(table.columns[4].data_type, Number)
        self.assertIsInstance(table.columns[5].data_type, Text)

        self.assertSequenceEqual(table.rows[0], [1, 'a', 'b', 'a', 2, 'c'])
        self.assertSequenceEqual(table.rows[1], [2, 'c', 'd', 'd', 2, 'f'])

    def test_from_csv_file_like_object(self):
        table = Table.from_csv('examples/test.csv', column_names, self.column_types)

        self.assertEqual(len(table.columns), 3)
        self.assertEqual(len(table.rows), 3)
        self.assertSequenceEqual(table.column_names, ['a', 'b', 'c'])

    def test_from_csv_file_like_object(self):
        table1 = Table.from_csv('examples/test.csv', self.column_names, self.column_types)

        with open('examples/test.csv') as fh:
            table2 = Table.from_csv(fh, self.column_names, self.column_types)

            self.assertSequenceEqual(table1.column_names, table2.column_names)
            self.assertSequenceEqual(table1.column_types, table2.column_types)

            self.assertEqual(len(table1.columns), len(table2.columns))
            self.assertEqual(len(table1.rows), len(table2.rows))

            self.assertSequenceEqual(table1.rows[0], table2.rows[0])
            self.assertSequenceEqual(table1.rows[1], table2.rows[1])
            self.assertSequenceEqual(table1.rows[2], table2.rows[2])

    def test_from_csv_type_tester(self):
        tester = TypeTester()

        output = Table.from_csv('examples/test.csv', column_types=tester)

        self.assertEqual(len(output.columns), 3)
        self.assertIsInstance(output.columns[0].data_type, Number)
        self.assertIsInstance(output.columns[1].data_type, Number)
        self.assertIsInstance(output.columns[2].data_type, Text)

    def test_from_csv_default_type_tester(self):
        output = Table.from_csv('examples/test.csv')

        self.assertEqual(len(output.columns), 3)
        self.assertIsInstance(output.columns[0].data_type, Number)
        self.assertIsInstance(output.columns[1].data_type, Number)
        self.assertIsInstance(output.columns[2].data_type, Text)

    def test_from_csv_no_header(self):
        output = Table.from_csv('examples/test_no_header.csv', header=False)

        self.assertEqual(len(output.columns), 3)
        self.assertSequenceEqual(output.column_names, ('A', 'B', 'C'))
        self.assertIsInstance(output.columns[0].data_type, Number)
        self.assertIsInstance(output.columns[1].data_type, Number)
        self.assertIsInstance(output.columns[2].data_type, Text)

    def test_from_csv_no_header_type_inference(self):
        output = Table.from_csv('examples/test_no_header.csv', header=False)

        self.assertEqual(len(output.columns), 3)
        self.assertSequenceEqual(output.column_names, ('A', 'B', 'C'))
        self.assertIsInstance(output.columns[0].data_type, Number)
        self.assertIsInstance(output.columns[1].data_type, Number)
        self.assertIsInstance(output.columns[2].data_type, Text)

    def test_to_csv(self):
        table = Table(self.rows, self.column_names, self.column_types)

        table.to_csv('.test.csv')

        with open('.test.csv') as f:
            contents1 = f.read()

        with open('examples/test.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

        os.remove('.test.csv')

    def test_to_csv_file_like_object(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with open('.test.csv', 'w') as f:
            table.to_csv(f)

            # Should leave the file open
            self.assertFalse(f.closed)

        with open('.test.csv') as f:
            contents1 = f.read()

        with open('examples/test.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

        os.remove('.test.csv')

    def test_to_csv_to_stdout(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.to_csv(output)

        contents1 = output.getvalue()

        with open('examples/test.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

    def test_get_column_types(self):
        table = Table(self.rows, self.column_names, self.column_types)

        self.assertSequenceEqual(table.column_types, self.column_types)

    def test_get_column_names(self):
        table = Table(self.rows, self.column_names, self.column_types)

        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_select(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.select(('three',))

        self.assertIsNot(new_table, table)

        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], ('a',))
        self.assertSequenceEqual(new_table.rows[1], ('b',))
        self.assertSequenceEqual(new_table.rows[2], (u'👍',))

        self.assertEqual(len(new_table.columns), 1)
        self.assertSequenceEqual(new_table._column_types, (self.text_type,))
        self.assertSequenceEqual(new_table._column_names, ('three',))
        self.assertSequenceEqual(new_table.columns['three'], ('a', 'b', u'👍'))

    def test_select_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.select(('three',))

        self.assertSequenceEqual(new_table.rows['a'], ('a',))
        self.assertSequenceEqual(new_table.row_names, ('a', 'b', u'👍'))

    def test_select_does_not_exist(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with self.assertRaises(KeyError):
            table.select(('four',))

    def test_where(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.where(lambda r: r['one'] in (2, None))

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.columns['one'], (2, None))

    def test_where_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.where(lambda r: r['one'] in (2, None))

        self.assertSequenceEqual(table.rows['a'], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.row_names, ('b', u'👍'))

    def test_find(self):
        table = Table(self.rows, self.column_names, self.column_types)

        row = table.find(lambda r: r['two'] - r['one'] == 1)

        self.assertIs(row, table.rows[1])

    def test_find_none(self):
        table = Table(self.rows, self.column_names, self.column_types)

        row = table.find(lambda r: r['one'] == 'FOO')

        self.assertIs(row, None)

    def test_order_by(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.order_by('two')

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (None, 2, u'👍'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (1, 4, 'a'))

        # Verify old table not changed
        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(table.rows[2], (None, 2, u'👍'))

    def test_order_by_nulls(self):
        self.rows = (
            (1, 4, 'a'),
            (None, 3, 'c'),
            (2, 3, 'b'),
            (None, 2, u'👍')
        )

        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.order_by('one')

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 3, 'c'))
        self.assertSequenceEqual(new_table.rows[3], (None, 2, u'👍'))

    def test_order_by_func(self):
        rows = (
            (1, 2, 'a'),
            (2, 1, 'b'),
            (1, 1, 'c')
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.order_by(lambda r: (r['one'], r['two']))

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 1, 'c'))
        self.assertSequenceEqual(new_table.rows[1], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.rows[2], (2, 1, 'b'))

    def test_order_by_reverse(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.order_by(lambda r: r['two'], reverse=True)

        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, u'👍'))

    def test_order_by_nulls(self):
        rows = (
            (1, 2, None),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, 'a')
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.order_by('two')

        self.assertSequenceEqual(new_table.columns['two'], (1, 2, None, None))

        new_table = table.order_by('three')

        self.assertSequenceEqual(new_table.columns['three'], ('a', 'c', None, None))

    def test_order_by_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.order_by('two')

        self.assertSequenceEqual(new_table.rows[u'a'], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.row_names, (u'👍', 'b', 'a'))

    def test_limit(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(2)

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.columns['one'], (1, 2))

    def test_limit_slice(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(0, 3, 2)

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (None, 2, u'👍'))
        self.assertSequenceEqual(new_table.columns['one'], (1, None))

    def test_limit_slice_negative(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(-2, step=-1)

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[1], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.columns['one'], (2, 1))

    def test_limit_step_only(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(step=2)

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (None, 2, u'👍'))
        self.assertSequenceEqual(new_table.columns['one'], (1, None))

    def test_limit_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.limit(2)

        self.assertSequenceEqual(new_table.rows['a'], (1, 4, 'a'))
        self.assertSequenceEqual(new_table.row_names, ('a', 'b'))

    def test_distinct_column(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.distinct('one')

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 2)
        self.assertSequenceEqual(new_table.rows[0], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, None, None))
        self.assertSequenceEqual(new_table.columns['one'], (1, 2))

    def test_distinct_func(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.distinct(lambda row: (row['two'], row['three']))

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, None, None))
        self.assertSequenceEqual(new_table.rows[2], (1, 1, 'c'))
        self.assertSequenceEqual(new_table.columns['one'], (1, 2, 1))

    def test_distinct_none(self):
        rows = (
            (1, 2, 'a'),
            (1, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.distinct()

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertSequenceEqual(new_table.rows[0], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (1, None, None))
        self.assertSequenceEqual(new_table.rows[2], (1, 1, 'c'))
        self.assertSequenceEqual(new_table.columns['one'], (1, 1, 1))

    def test_distinct_with_row_names(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, 'd')
        )

        table = Table(rows, self.column_names, self.column_types, row_names='three')
        new_table = table.distinct('one')

        self.assertSequenceEqual(new_table.rows['a'], (1, 2, 'a'))
        self.assertSequenceEqual(new_table.row_names, ('a', None))

    def test_chain_select_where(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.select(('one', 'two')).where(lambda r: r['two'] == 3)

        self.assertEqual(len(new_table.rows), 1)
        self.assertSequenceEqual(new_table.rows[0], (2, 3))

        self.assertEqual(len(new_table.columns), 2)
        self.assertSequenceEqual(new_table._column_types, (self.number_type, self.number_type))
        self.assertEqual(new_table._column_names, ('one', 'two'))
        self.assertSequenceEqual(new_table.columns['one'], (2,))

class TestCounts(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 'Y'),
            (2, 'N'),
            (2, 'N'),
            (1, 'N'),
            (None, None),
            (3, 'N')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two']
        self.column_types = [self.number_type, self.text_type]

    def test_counts_numbers(self):
        table = Table(self.rows, self.column_names, self.column_types)
        new_table = table.counts('one')

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 2)

        self.assertSequenceEqual(new_table.rows[0], [1, 2])
        self.assertSequenceEqual(new_table.rows[1], [2, 2])
        self.assertSequenceEqual(new_table.rows[2], [None, 1])
        self.assertSequenceEqual(new_table.rows[3], [3, 1])

    def test_counts_text(self):
        table = Table(self.rows, self.column_names, self.column_types)
        new_table = table.counts('two')

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 2)

        self.assertSequenceEqual(new_table.rows[0], ['Y', 1])
        self.assertSequenceEqual(new_table.rows[1], ['N', 4])
        self.assertSequenceEqual(new_table.rows[2], [None, 1])

        self.assertSequenceEqual(new_table.row_names, ['Y', 'N', None])

    def test_counts_key_func(self):
        table = Table(self.rows, self.column_names, self.column_types)
        new_table = table.counts(lambda r: r['two'])

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 2)

        self.assertSequenceEqual(new_table.rows[0], ['Y', 1])
        self.assertSequenceEqual(new_table.rows[1], ['N', 4])
        self.assertSequenceEqual(new_table.rows[2], [None, 1])

        self.assertSequenceEqual(new_table.row_names, ['Y', 'N', None])

class TestBins(unittest.TestCase):
    def setUp(self):
        self.number_type = Number()
        self.column_names = ['number']
        self.column_types = [self.number_type]

    def test_bins(self):
        rows = []

        for i in range(0, 100):
            rows.append([i]),

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertSequenceEqual(new_table.rows[0], ['[0 - 10)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[30 - 40)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[90 - 100]', 10])

        self.assertSequenceEqual(new_table.row_names, [
            '[0 - 10)',
            '[10 - 20)',
            '[20 - 30)',
            '[30 - 40)',
            '[40 - 50)',
            '[50 - 60)',
            '[60 - 70)',
            '[70 - 80)',
            '[80 - 90)',
            '[90 - 100]',
        ])

    def test_bins_negative(self):
        rows = []

        for i in range(0, -100, -1):
            rows.append([i])

        new_table = Table(rows, self.column_names, self.column_types).bins('number', 10, -100, 0)

        self.assertSequenceEqual(new_table.rows[0], ['[-100 - -90)', 9])
        self.assertSequenceEqual(new_table.rows[3], ['[-70 - -60)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[-10 - 0]', 11])

    def test_bins_mixed_signs(self):
        rows = []

        for i in range(0, -100, -1):
            rows.append([i + 50])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertSequenceEqual(new_table.rows[0], ['[-50 - -40)', 9])
        self.assertSequenceEqual(new_table.rows[3], ['[-20 - -10)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[40 - 50]', 11])

    def test_bins_small_numbers(self):
        rows = []

        for i in range(0, 100):
            rows.append([Decimal(i) / Decimal('10')])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertSequenceEqual(new_table.rows[0], ['[0 - 1)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[3 - 4)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[9 - 10]', 10])

    def test_bins_decimals(self):
        rows = []

        for i in range(0, 100):
            rows.append([Decimal(i) / Decimal('100')])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertSequenceEqual(new_table.rows[0], ['[0.0 - 0.1)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[0.3 - 0.4)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[0.9 - 1.0]', 10])

    def test_bins_nulls(self):
        rows = []

        for i in range(0, 100):
            rows.append([Decimal(i) / Decimal('100')])

        rows.append([None])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertSequenceEqual(new_table.rows[0], ['[0.0 - 0.1)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[0.3 - 0.4)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[0.9 - 1.0]', 10])
        self.assertSequenceEqual(new_table.rows[10], [None, 1])

class TestPrettyPrint(unittest.TestCase):
    def setUp(self):
        self.rows = (
            ('1.7', 2, 'a'),
            ('11.18', None, None),
            ('0', 1, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

    def test_print_table(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_table(output=output)
        lines = output.getvalue().split('\n')

        self.assertEqual(len(lines), 8)
        self.assertEqual(len(lines[0]), 25)

    def test_print_csv(self):
        rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, u'👍')
        )

        table = Table(rows, self.column_names, self.column_types)

        old = sys.stdout
        sys.stdout = StringIO()

        try:
            table.print_csv()

            contents1 = sys.stdout.getvalue()

            with open('examples/test.csv') as f:
                contents2 = f.read()

            self.assertEqual(contents1, contents2)
        finally:
            sys.stdout = old

    def test_print_table_max_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_table(max_rows=2, output=output)
        lines = output.getvalue().split('\n')

        self.assertEqual(len(lines), 8)
        self.assertEqual(len(lines[0]), 25)

    def test_print_table_max_columns(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_table(max_columns=2, output=output)
        lines = output.getvalue().split('\n')

        self.assertEqual(len(lines), 8)
        self.assertEqual(len(lines[0]), 23)

    def test_print_bars(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_bars('three', 'one', output=output)
        lines = output.getvalue().split('\n')

    def test_print_bars_width(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_bars('three', 'one', width=40, output=output)
        lines = output.getvalue().split('\n')

        self.assertEqual(max([len(l) for l in lines]), 40)

    def test_print_bars_width_overlap(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_bars('three', 'one', width=20, output=output)
        lines = output.getvalue().split('\n')

        self.assertEqual(max([len(l) for l in lines]), 20)

    def test_print_bars_domain(self):
        table = Table(self.rows, self.column_names, self.column_types)

        table.print_bars('three', 'one', domain=(0, 300))

    def test_print_bars_domain_invalid(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with self.assertRaises(ValueError):
            table.print_bars('three', 'one', domain=(5, 0))

    def test_print_bars_negative(self):
        rows = (
            ('-1.7', 2, 'a'),
            ('-11.18', None, None),
            ('0', 1, 'c')
        )

        table = Table(rows, self.column_names, self.column_types)
        table.print_bars('three', 'one')

    def test_print_bars_mixed_signs(self):
        rows = (
            ('-1.7', 2, 'a'),
            ('11.18', None, None),
            ('0', 1, 'c')
        )

        table = Table(rows, self.column_names, self.column_types)
        table.print_bars('three', 'one')

    def test_print_bars_invalid_values(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with self.assertRaises(DataTypeError):
            table.print_bars('one', 'three')

class TestTableGrouping(unittest.TestCase):
    def setUp(self):
        self.rows = (
            ('a', 2, 3, 4),
            (None, 3, 5, None),
            ('a', 2, 4, None),
            ('b', 3, 4, None)
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = [
            'one', 'two', 'three', 'four'
        ]
        self.column_types = [
            self.text_type, self.number_type, self.number_type, self.number_type
        ]

    def test_group_by(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by('one')

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(len(tableset), 3)
        self.assertEqual(tableset.key_name, 'one')
        self.assertIsInstance(tableset.key_type, Text)

        self.assertIn('a', tableset.keys())
        self.assertIn('b', tableset.keys())
        self.assertIn(None, tableset.keys())

        self.assertSequenceEqual(tableset['a'].columns['one'], ('a', 'a'))
        self.assertSequenceEqual(tableset['b'].columns['one'], ('b',))

    def test_group_by_number(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by('two')

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(len(tableset), 2)
        self.assertEqual(tableset.key_name, 'two')
        self.assertIsInstance(tableset.key_type, Number)

        self.assertIn(Decimal('2'), tableset.keys())
        self.assertIn(Decimal('3'), tableset.keys())

        self.assertSequenceEqual(tableset[Decimal('2')].columns['one'], ('a', 'a'))
        self.assertSequenceEqual(tableset[Decimal('3')].columns['one'], (None, 'b'))

    def test_group_by_key_name(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by('one', key_name='test')

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(tableset.key_name, 'test')
        self.assertIsInstance(tableset.key_type, Text)

        self.assertIn('a', tableset.keys())
        self.assertIn('b', tableset.keys())
        self.assertIn(None, tableset.keys())

        self.assertSequenceEqual(tableset['a'].columns['one'], ('a', 'a'))
        self.assertSequenceEqual(tableset['b'].columns['one'], ('b',))

    def test_group_by_key_type(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by('two', key_type=Text())

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(tableset.key_name, 'two')
        self.assertIsInstance(tableset.key_type, Text)

        self.assertIn('2', tableset.keys())
        self.assertIn('3', tableset.keys())

        self.assertSequenceEqual(tableset['2'].columns['one'], ('a', 'a'))
        self.assertSequenceEqual(tableset['3'].columns['one'], (None, 'b'))

    def test_group_by_function(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by(lambda r: r['three'] < 5, key_type=Boolean())

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(len(tableset), 2)
        self.assertEqual(tableset.key_name, 'group')

        self.assertIn(True, tableset.keys())
        self.assertIn(False, tableset.keys())

        self.assertSequenceEqual(tableset[True].columns['one'], ('a', 'a', 'b'))
        self.assertSequenceEqual(tableset[False].columns['one'], (None,))

    def test_group_by_bad_column(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with self.assertRaises(KeyError):
            table.group_by('bad')

class TestTableCompute(unittest.TestCase):
    def setUp(self):
        self.rows = (
            ('a', 2, 3, 4),
            (None, 3, 5, None),
            ('a', 2, 4, None),
            ('b', 3, 6, None)
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = [
            'one', 'two', 'three', 'four'
        ]
        self.column_types = [
            self.text_type, self.number_type, self.number_type, self.number_type
        ]

        self.table = Table(self.rows, self.column_names, self.column_types)

    def test_compute(self):
        new_table = self.table.compute([
            (Formula(self.number_type, lambda r: r['two'] + r['three']), 'number'),
            (Formula(self.text_type, lambda r: (r['one'] or '-') + six.text_type(r['three'])), 'text')
        ])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 6)

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 5, 'a3'))
        self.assertSequenceEqual(new_table.columns['number'], (5, 8, 6, 9))
        self.assertSequenceEqual(new_table.columns['text'], ('a3', '-5', 'a4', 'b6'))

    def test_compute_multiple(self):
        new_table = self.table.compute([
            (Formula(self.number_type, lambda r: r['two'] + r['three']), 'test')
        ])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 5))
        self.assertSequenceEqual(new_table.columns['test'], (5, 8, 6, 9))

    def test_compute_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')

        new_table = table.compute([
            (Formula(self.number_type, lambda r: r['two'] + r['three']), 'number'),
            (Formula(self.text_type, lambda r: (r['one'] or '-') + six.text_type(r['three'])), 'text')
        ])

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 5, 'a3'))
        self.assertSequenceEqual(new_table.row_names, (3, 5, 4, 6))

class TestTableJoin(unittest.TestCase):
    def setUp(self):
        self.left_rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )

        self.right_rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.left_column_names = ['one', 'two', 'three']
        self.right_column_names = ['four', 'five', 'six']
        self.column_types = [self.number_type, self.number_type, self.text_type]

        self.left = Table(self.left_rows, self.left_column_names, self.column_types)
        self.right = Table(self.right_rows, self.right_column_names, self.column_types)

    def test_join(self):
        new_table = self.left.join(self.right, 'one', 'four')

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 5)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'five')
        self.assertEqual(new_table.columns[4].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Text)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', 2, 'c'))

    def test_join_match_multiple(self):
        left_rows = (
            (1, 4, 'a'),
            (2, 3, 'b')
        )

        right_rows = (
            (1, 1, 'a'),
            (1, 2, 'a'),
            (2, 2, 'b')
        )

        left = Table(left_rows, self.left_column_names, self.column_types)
        right = Table(right_rows, self.right_column_names, self.column_types)
        new_table = left.join(right, 'one', 'five')

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 5)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'four')
        self.assertEqual(new_table.columns[4].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Text)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', 1, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', 1, 'a'))
        self.assertSequenceEqual(new_table.rows[2], (2, 3, 'b', 2, 'b'))

    def test_join2(self):
        new_table = self.left.join(self.right, 'one', 'five')

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 5)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'four')
        self.assertEqual(new_table.columns[4].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Text)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', None, None))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', None, 'c'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', None, None))

    def test_join_same_column_name(self):
        right_column_names = ['four', 'one', 'six']

        right = Table(self.right_rows, right_column_names, self.column_types)

        new_table = self.left.join(right, 'one')

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 5)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'four')
        self.assertEqual(new_table.columns[4].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Text)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', None, None))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', None, 'c'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', None, None))

    def test_join_func(self):
        new_table = self.left.join(
            self.right,
            lambda left: '%i%s' % (left['two'], left['three']),
            lambda right: '%i%s' % (right['five'], right['six'])
        )

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 6)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'four')
        self.assertEqual(new_table.columns[4].name, 'five')
        self.assertEqual(new_table.columns[5].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Number)
        self.assertIsInstance(new_table.columns[5].data_type, Text)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', 1, 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', 2, 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', None, 2, 'c'))

    def test_join_column_does_not_exist(self):
        with self.assertRaises(KeyError):
            self.left.join(self.right, 'one', 'seven')

    def test_inner_join(self):
        new_table = self.left.join(self.right, 'one', 'four', inner=True)

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 5)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'five')
        self.assertEqual(new_table.columns[4].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Text)

        self.assertSequenceEqual(new_table.rows[0], (1, 4, 'a', 4, 'a'))
        self.assertSequenceEqual(new_table.rows[1], (2, 3, 'b', 3, 'b'))
        self.assertSequenceEqual(new_table.rows[2], (None, 2, 'c', 2, 'c'))

    def test_inner_join2(self):
        new_table = self.left.join(self.right, 'one', 'five', inner=True)

        self.assertEqual(len(new_table.rows), 1)
        self.assertEqual(len(new_table.columns), 5)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'four')
        self.assertEqual(new_table.columns[4].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Text)

        self.assertSequenceEqual(new_table.rows[0], (2, 3, 'b', None, 'c'))

    def test_inner_join_same_column_name(self):
        right_column_names = ['four', 'one', 'six']

        right = Table(self.right_rows, right_column_names, self.column_types)

        new_table = self.left.join(right, 'one', inner=True)

        self.assertEqual(len(new_table.rows), 1)
        self.assertEqual(len(new_table.columns), 5)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'four')
        self.assertEqual(new_table.columns[4].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Text)

        self.assertSequenceEqual(new_table.rows[0], (2, 3, 'b', None, 'c'))

    def test_inner_join_func(self):
        new_table = self.left.join(
            self.right,
            lambda left: '%i%s' % (left['two'], left['three']),
            lambda right: '%i%s' % (right['five'], right['six']),
            inner=True
        )

        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 6)

        self.assertEqual(new_table.columns[0].name, 'one')
        self.assertEqual(new_table.columns[1].name, 'two')
        self.assertEqual(new_table.columns[2].name, 'three')
        self.assertEqual(new_table.columns[3].name, 'four')
        self.assertEqual(new_table.columns[4].name, 'five')
        self.assertEqual(new_table.columns[5].name, 'six')

        self.assertIsInstance(new_table.columns[0].data_type, Number)
        self.assertIsInstance(new_table.columns[1].data_type, Number)
        self.assertIsInstance(new_table.columns[2].data_type, Text)
        self.assertIsInstance(new_table.columns[3].data_type, Number)
        self.assertIsInstance(new_table.columns[4].data_type, Number)
        self.assertIsInstance(new_table.columns[5].data_type, Text)

    def test_join_with_row_names(self):
        left = Table(self.left_rows, self.left_column_names, self.column_types, row_names='three')
        new_table = left.join(self.right, 'one', 'four')

        self.assertSequenceEqual(new_table.rows['a'], (1, 4, 'a', 4, 'a'))
        self.assertSequenceEqual(new_table.row_names, ('a', 'b', 'c'))

class TestTableMerge(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

    def test_merge(self):
        table_a = Table(self.rows, self.column_names, self.column_types)
        table_b = Table(self.rows, self.column_names, self.column_types)
        table_c = Table.merge([table_a, table_b])

        self.assertEqual(table_c.column_names, table_a.column_names)
        self.assertEqual(table_c.column_types, table_a.column_types)

        self.assertEqual(len(table_c.rows), 6)

    def test_merge_different_names(self):
        table_a = Table(self.rows, self.column_names, self.column_types)

        column_types = [self.number_type, self.number_type, self.text_type]

        table_b = Table(self.rows, self.column_names, column_types)
        table_c = Table.merge([table_a, table_b])

        self.assertEqual(table_c.column_names, table_a.column_names)
        self.assertEqual(table_c.column_types, table_a.column_types)

        self.assertEqual(len(table_c.rows), 6)

    def test_merge_different_types(self):
        table_a = Table(self.rows, self.column_names, self.column_types)

        column_types = [self.number_type, self.text_type, self.text_type]

        table_b = Table(self.rows, self.column_names, column_types)

        with self.assertRaises(ValueError):
            table_c = Table.merge([table_a, table_b])

    def test_merge_with_row_names(self):
        table_a = Table(self.rows, self.column_names, self.column_types, row_names='three')
        table_b = Table(self.rows, self.column_names, self.column_types)
        table_c = Table.merge([table_a, table_b])

        self.assertEqual(table_a.row_names, table_c.row_names)

class TestTableData(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

    def test_data_immutable(self):
        rows = [
            [1, 4, 'a'],
            [2, 3, 'b'],
            [None, 2, 'c']
        ]

        table = Table(rows, self.column_names, self.column_types)
        rows[0] = [2, 2, 2]
        self.assertSequenceEqual(table.rows[0], [1, 4, 'a'])

    def test_fork_preserves_data(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table._fork(table.rows)

        self.assertIs(table.rows[0], table2.rows[0])
        self.assertIs(table.rows[1], table2.rows[1])
        self.assertIs(table.rows[2], table2.rows[2])

    def test_where_preserves_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.where(lambda r: r['one'] == 1)
        table3 = table2.where(lambda r: r['one'] == 1)

        self.assertIs(table.rows[0], table2.rows[0])
        self.assertIs(table2.rows[0], table3.rows[0])

    def test_order_by_preserves_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.order_by(lambda r: r['one'])
        table3 = table2.order_by(lambda r: r['one'])

        self.assertIs(table.rows[0], table2.rows[0])
        self.assertIs(table2.rows[0], table3.rows[0])

    def test_limit_preserves_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.limit(2)
        table3 = table2.limit(2)

        self.assertIs(table.rows[0], table2.rows[0])
        self.assertIs(table2.rows[0], table3.rows[0])

    def test_compute_creates_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.compute([
            (Formula(self.number_type, lambda r: r['one']), 'new2')
        ])
        table3 = table2.compute([
            (Formula(self.number_type, lambda r: r['one']), 'new3')
        ])

        self.assertIsNot(table.rows[0], table2.rows[0])
        self.assertNotEqual(table.rows[0], table2.rows[0])
        self.assertIsNot(table2.rows[0], table3.rows[0])
        self.assertNotEqual(table2.rows[0], table3.rows[0])
        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))
