#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

import json

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import os
import sys

import six
from six.moves import html_parser
from six.moves import range

from agate import Table, TableSet
from agate.aggregations import Length, Sum
from agate.data_types import *
from agate.computations import Formula
from agate.exceptions import DataTypeError
from agate.testcase import AgateTestCase

class TestBasic(AgateTestCase):
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
        table = Table(self.rows)

        self.assertColumnNames(table, ['A', 'B', 'C'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_table_column_types(self):
        column_types = [self.number_type, self.text_type, self.text_type]
        table = Table(self.rows, column_types=column_types)

        self.assertColumnNames(table, ['A', 'B', 'C'])
        self.assertColumnTypes(table, [Number, Text, Text])
        self.assertRows(table, [
            (1, '4', 'a'),
            (2, '3', 'b'),
            (None, '2', u'👍')
        ])

    def test_create_table_column_names(self):
        table = Table(self.rows, self.column_names)

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_table_column_types_and_names(self):
        table = Table(self.rows, self.column_names, self.column_types)

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

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

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, [
            (1, 4, 'a'),
            (2, None, None),
            (None, 2, None)
        ])

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

        self.assertRowNames(table, ['a', 'b', u'👍'])

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

    def test_row_names_invalid(self):

        with self.assertRaises(ValueError):
            table = Table(
                self.rows,
                self.column_names,
                self.column_types,
                row_names={ 'a': 1, 'b': 2, 'c': 3 }
            )

    def test_stringify(self):
        column_names = ['foo', 'bar', u'👍']

        table = Table(self.rows, column_names)

        if six.PY2:
            u = unicode(table)

            self.assertIn('foo', u)
            self.assertIn('bar', u)
            self.assertIn(u'👍', u)

            s = str(table)

            self.assertIn('foo', s)
            self.assertIn('bar', s)
            self.assertIn(u'👍'.encode('utf-8'), s)
        else:
            u = str(table)

            self.assertIn('foo', u)
            self.assertIn('bar', u)
            self.assertIn(u'👍', u)

    def test_str(self):
        table = Table(self.rows)

        self.assertColumnNames(table, ['A', 'B', 'C'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

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

        self.assertColumnNames(new_table, ['three'])
        self.assertColumnTypes(new_table, [Text])
        self.assertRows(new_table,[
            ['a'],
            ['b'],
            [u'👍']
        ])

    def test_select_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.select(('three',))

        self.assertRowNames(new_table, ['a', 'b', u'👍'])

    def test_select_does_not_exist(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with self.assertRaises(KeyError):
            table.select(('four',))

    def test_exclude(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.exclude(('one', 'two'))

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, ['three'])
        self.assertColumnTypes(new_table, [Text])
        self.assertRows(new_table,[
            ['a'],
            ['b'],
            [u'👍']
        ])

    def test_exclude_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.exclude(('one', 'two'))

        self.assertRowNames(new_table, ['a', 'b', u'👍'])

    def test_where(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.where(lambda r: r['one'] in (2, None))

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table,[
            self.rows[1],
            self.rows[2]
        ])

    def test_where_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.where(lambda r: r['one'] in (2, None))

        self.assertRowNames(new_table, ['b', u'👍'])

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

        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table,[
            self.rows[2],
            self.rows[1],
            self.rows[0]
        ])

        # Verify old table not changed
        self.assertRows(table, self.rows)

    def test_order_by_func(self):
        rows = (
            (1, 2, 'a'),
            (2, 1, 'b'),
            (1, 1, 'c')
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.order_by(lambda r: (r['one'], r['two']))


        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table,[
            rows[2],
            rows[0],
            rows[1]
        ])

    def test_order_by_reverse(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.order_by(lambda r: r['two'], reverse=True)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table,[
            self.rows[0],
            self.rows[1],
            self.rows[2]
        ])

    def test_order_by_nulls(self):
        rows = (
            (1, 2, None),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, 'a')
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.order_by('two')

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[2],
            rows[0],
            rows[1],
            rows[3]
        ])

        new_table = table.order_by('three')

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[3],
            rows[2],
            rows[0],
            rows[1]
        ])

    def test_order_by_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.order_by('two')

        self.assertRowNames(new_table, [u'👍', 'b', 'a'])

    def test_limit(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(2)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, self.rows[:2])

    def test_limit_slice(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(0, 3, 2)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, self.rows[0:3:2])

    def test_limit_slice_negative(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(-2, step=-1)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, self.rows[-2:-1])

    def test_limit_step_only(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.limit(step=2)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, self.rows[::2])

    def test_limit_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')
        new_table = table.limit(2)

        self.assertRowNames(new_table, ['a', 'b'])

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
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[0],
            rows[1]
        ])

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
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[0],
            rows[1],
            rows[2]
        ])

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
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[0],
            rows[1],
            rows[2]
        ])

    def test_distinct_with_row_names(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, 'd')
        )

        table = Table(rows, self.column_names, self.column_types, row_names='three')
        new_table = table.distinct('one')

        self.assertRowNames(new_table, ['a', None])

    def test_chain_select_where(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.select(('one', 'two')).where(lambda r: r['two'] == 3)

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names[:2])
        self.assertColumnTypes(new_table, [Number, Number])
        self.assertRows(new_table, [
            self.rows[1][:2],
        ])

class TestCSV(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 'a', True, '11/4/2015', '11/4/2015 12:22 PM', '4:15'),
            (2, u'👍', False, '11/5/2015', '11/4/2015 12:45 PM', '6:18'),
            (None, 'b', None, None, None, None)
        )

        self.column_names = [
            'number', 'text', 'boolean', 'date', 'datetime', 'timedelta'
        ]

        self.column_types = [
            Number(), Text(), Boolean(), Date(), DateTime(), TimeDelta()
        ]

    def test_from_csv(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test.csv')

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_file_like_object(self):
        table1 = Table(self.rows, self.column_names, self.column_types)

        with open('examples/test.csv') as f:
            table2 = Table.from_csv(f)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_type_tester(self):
        tester = TypeTester(force={
            'number': Text()
        })

        table = Table.from_csv('examples/test.csv', column_types=tester)

        self.assertColumnTypes(table, [Text, Text, Boolean, Date, DateTime, TimeDelta])

    def test_from_csv_no_header(self):
        table = Table.from_csv('examples/test_no_header.csv', header=False)

        self.assertColumnNames(table, ['A', 'B', 'C', 'D', 'E', 'F'])
        self.assertColumnTypes(table, [Number, Text, Boolean, Date, DateTime, TimeDelta])

    def test_from_csv_no_header_columns(self):
        table = Table.from_csv('examples/test_no_header.csv', self.column_names, header=False)

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Text, Boolean, Date, DateTime, TimeDelta])

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

    def test_to_csv_make_dir(self):
        table = Table(self.rows, self.column_names, self.column_types)

        table.to_csv('newdir/test.csv')

        with open('newdir/test.csv') as f:
            contents1 = f.read()

        with open('examples/test.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

        os.remove('newdir/test.csv')
        os.rmdir('newdir/')

    def test_print_csv(self):
        table = Table(self.rows, self.column_names, self.column_types)

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

class TestJSON(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 'a', True, '11/4/2015', '11/4/2015 12:22 PM', '4:15'),
            (2, u'👍', False, '11/5/2015', '11/4/2015 12:45 PM', '6:18'),
            (None, 'b', None, None, None, None)
        )

        self.column_names = [
            'number', 'text', 'boolean', 'date', 'datetime', 'timedelta'
        ]

        self.column_types = [
            Number(), Text(), Boolean(), Date(), DateTime(), TimeDelta()
        ]
    def test_from_json(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_json('examples/test.json')

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])
        self.assertRows(table2, table1.rows)

    def test_from_json_file_like_object(self):
        table1 = Table(self.rows, self.column_names, self.column_types)

        with open('examples/test.json') as f:
            table2 = Table.from_json(f)

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])
        self.assertRows(table2, table1.rows)

    def test_from_json_with_key(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_json('examples/test_key.json', key='data')

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])
        self.assertRows(table2, table1.rows)

    def test_from_json_mixed_keys(self):
        table = Table.from_json('examples/test_mixed.json')

        self.assertColumnNames(table, ['one', 'two', 'three', 'four', 'five'])
        self.assertColumnTypes(table, [Number, Number, Text, Text, Number])
        self.assertRows(table, [
            [1, 4, 'a', None, None],
            [2, 3, 'b', 'd', None],
            [None, 2, u'👍', None, 5]
        ])

    def test_from_json_nested(self):
        table = Table.from_json('examples/test_nested.json')

        self.assertColumnNames(table, ['one', 'two/two_a', 'two/two_b', 'three/0', 'three/1', 'three/2'])
        self.assertColumnTypes(table, [Number, Text, Text, Text, Number, Text])
        self.assertRows(table, [
            [1, 'a', 'b', 'a', 2, 'c'],
            [2, 'c', 'd', 'd', 2, 'f']
        ])

    def test_from_json_newline_delimited(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_json('examples/test_newline.json', newline=True)

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])
        self.assertRows(table2, table1.rows)

    def test_to_json(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.to_json(output, indent=4)

        js1 = json.loads(output.getvalue())

        with open('examples/test.json') as f:
            js2 = json.load(f)

        self.assertEqual(js1, js2)

    def test_to_json_key(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.to_json(output, key='text', indent=4)

        js1 = json.loads(output.getvalue())

        with open('examples/test_keyed.json') as f:
            js2 = json.load(f)

        self.assertEqual(js1, js2)

    def test_to_json_key_func(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.to_json(output, key=lambda r: r['text'], indent=4)

        js1 = json.loads(output.getvalue())

        with open('examples/test_keyed.json') as f:
            js2 = json.load(f)

        self.assertEqual(js1, js2)

    def test_to_json_newline_delimited(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.to_json(output, newline=True)

        js1 = json.loads(output.getvalue().split('\n')[0])

        with open('examples/test_newline.json') as f:
            js2 = json.loads(list(f)[0])

        self.assertEqual(js1, js2)

    def test_to_json_error_newline_indent(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()

        with self.assertRaises(ValueError):
            table.to_json(output, newline=True, indent=4)

    def test_to_json_error_newline_key(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()

        with self.assertRaises(ValueError):
            table.to_json(output, key='three', newline=True)

    def test_to_json_file_output(self):
        table = Table(self.rows, self.column_names, self.column_types)

        table.to_json('.test.json')

        with open('.test.json') as f1:
            js1 = json.load(f1)

        with open('examples/test.json') as f2:
            js2 = json.load(f2)

        self.assertEqual(js1, js2)

        os.remove('.test.json')

    def test_to_json_make_dir(self):
        table = Table(self.rows, self.column_names, self.column_types)

        table.to_json('newdir/test.json')

        with open('newdir/test.json') as f1:
            js1 = json.load(f1)

        with open('examples/test.json') as f2:
            js2 = json.load(f2)

        self.assertEqual(js1, js2)

        os.remove('newdir/test.json')
        os.rmdir('newdir/')

    def test_print_json(self):
        table = Table(self.rows, self.column_names, self.column_types)

        old = sys.stdout
        sys.stdout = StringIO()

        try:
            table.print_json()

            js1 = json.loads(sys.stdout.getvalue())

            with open('examples/test.json') as f:
                js2 = json.load(f)

            self.assertEqual(js1, js2)
        finally:
            sys.stdout = old

class TestCounts(AgateTestCase):
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

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, ['one', 'count'])
        self.assertColumnTypes(new_table, [Number, Number])
        self.assertRowNames(new_table, [1, 2, None, 3])
        self.assertRows(new_table, [
            [1, 2],
            [2, 2],
            [None, 1],
            [3, 1]
        ])

    def test_counts_text(self):
        table = Table(self.rows, self.column_names, self.column_types)
        new_table = table.counts('two')

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, ['two', 'count'])
        self.assertColumnTypes(new_table, [Text, Number])
        self.assertRowNames(new_table, ['Y', 'N', None])
        self.assertRows(new_table, [
            ['Y', 1],
            ['N', 4],
            [None, 1]
        ])

    def test_counts_key_func(self):
        table = Table(self.rows, self.column_names, self.column_types)
        new_table = table.counts(lambda r: r['two'])

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, ['group', 'count'])
        self.assertColumnTypes(new_table, [Text, Number])
        self.assertRowNames(new_table, ['Y', 'N', None])
        self.assertRows(new_table, [
            ['Y', 1],
            ['N', 4],
            [None, 1]
        ])

class TestBins(AgateTestCase):
    def setUp(self):
        self.number_type = Number()
        self.column_names = ['number']
        self.column_types = [self.number_type]

    def test_bins(self):
        rows = []

        for i in range(0, 100):
            rows.append([i]),

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertColumnNames(new_table, ['number', 'count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(new_table.rows[0], ['[0 - 10)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[30 - 40)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[90 - 100]', 10])

        self.assertRowNames(new_table, [
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

        self.assertColumnNames(new_table, ['number', 'count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(new_table.rows[0], ['[-100 - -90)', 9])
        self.assertSequenceEqual(new_table.rows[3], ['[-70 - -60)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[-10 - 0]', 11])

    def test_bins_mixed_signs(self):
        rows = []

        for i in range(0, -100, -1):
            rows.append([i + 50])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertColumnNames(new_table, ['number', 'count'])
        self.assertColumnTypes(new_table, [Text, Number])

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

        self.assertColumnNames(new_table, ['number', 'count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(new_table.rows[0], ['[0.0 - 0.1)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[0.3 - 0.4)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[0.9 - 1.0]', 10])

    def test_bins_nulls(self):
        rows = []

        for i in range(0, 100):
            rows.append([Decimal(i) / Decimal('100')])

        rows.append([None])

        new_table = Table(rows, self.column_names, self.column_types).bins('number')

        self.assertColumnNames(new_table, ['number', 'count'])
        self.assertColumnTypes(new_table, [Text, Number])

        self.assertSequenceEqual(new_table.rows[0], ['[0.0 - 0.1)', 10])
        self.assertSequenceEqual(new_table.rows[3], ['[0.3 - 0.4)', 10])
        self.assertSequenceEqual(new_table.rows[9], ['[0.9 - 1.0]', 10])
        self.assertSequenceEqual(new_table.rows[10], [None, 1])

class TestPrettyPrint(AgateTestCase):
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

    def test_print_html(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_html(output=output)
        html = output.getvalue()

        self.assertEqual(html.count('<tr>'), 4)
        self.assertEqual(html.count('<th>'), 3)
        self.assertEqual(html.count('<td>'), 9)

    def test_print_html_max_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_html(max_rows=2, output=output)
        html = output.getvalue()

        self.assertEqual(html.count('<tr>'), 3)
        self.assertEqual(html.count('<th>'), 3)
        self.assertEqual(html.count('<td>'), 6)

    def test_print_html_max_columns(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_html(max_columns=2, output=output)
        html = output.getvalue()

        self.assertEqual(html.count('<tr>'), 4)
        self.assertEqual(html.count('<th>'), 2)
        self.assertEqual(html.count('<td>'), 6)

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

    def test_print_structure(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.print_structure(output=output)
        lines = output.getvalue().strip().split('\n')

        self.assertEqual(len(lines), 7)

class TestGrouping(AgateTestCase):
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

class TestAggregate(AgateTestCase):
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

        self.table = Table(self.rows, self.column_names, self.column_types)

    def test_length(self):
        self.assertEqual(self.table.aggregate(Length()), 3)

    def test_sum(self):
        self.assertEqual(self.table.aggregate(Sum('two')), 9)

    def test_multiple(self):
        self.assertSequenceEqual(
            self.table.aggregate([
                Length(),
                Sum('two')
            ]),
            [3, 9]
        )

class TestCompute(AgateTestCase):
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
            ('test', Formula(self.number_type, lambda r: r['two'] + r['three']))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'test'])
        self.assertColumnTypes(new_table, [Text, Number, Number, Number, Number])

        print(new_table.rows[0])
        print(new_table.columns['test'])

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 5))
        self.assertSequenceEqual(new_table.columns['test'], (5, 8, 6, 9))

    def test_compute_multiple(self):
        new_table = self.table.compute([
            ('number', Formula(self.number_type, lambda r: r['two'] + r['three'])),
            ('text', Formula(self.text_type, lambda r: (r['one'] or '-') + six.text_type(r['three'])))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'number', 'text'])
        self.assertColumnTypes(new_table, [Text, Number, Number, Number, Number, Text])

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 5, 'a3'))
        self.assertSequenceEqual(new_table.columns['number'], (5, 8, 6, 9))
        self.assertSequenceEqual(new_table.columns['text'], ('a3', '-5', 'a4', 'b6'))

    def test_compute_with_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names='three')

        new_table = table.compute([
            ('number', Formula(self.number_type, lambda r: r['two'] + r['three'])),
            ('text', Formula(self.text_type, lambda r: (r['one'] or '-') + six.text_type(r['three'])))
        ])

        self.assertRowNames(new_table, [3, 5, 4, 6])

class TestJoin(AgateTestCase):
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

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 4, 'a'),
            (2, 3, 'b', 3, 'b'),
            (None, 2, 'c', 2, 'c')
        ])

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

        self.assertIsNot(new_table, left)
        self.assertIsNot(new_table, right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 'a'),
            (2, 3, 'b', 1, 'a'),
            (2, 3, 'b', 2, 'b')
        ])

    def test_join2(self):
        new_table = self.left.join(self.right, 'one', 'five')

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', None, None),
            (2, 3, 'b', None, 'c'),
            (None, 2, 'c', None, None)
        ])

    def test_join_same_column_name(self):
        right_column_names = ['four', 'one', 'six']

        right = Table(self.right_rows, right_column_names, self.column_types)

        new_table = self.left.join(right, 'one')

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', None, None),
            (2, 3, 'b', None, 'c'),
            (None, 2, 'c', None, None)
        ])

    def test_join_func(self):
        new_table = self.left.join(
            self.right,
            lambda left: '%i%s' % (left['two'], left['three']),
            lambda right: '%i%s' % (right['five'], right['six'])
        )

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 4, 'a'),
            (2, 3, 'b', 2, 3, 'b'),
            (None, 2, 'c', None, 2, 'c')
        ])

    def test_join_column_does_not_exist(self):
        with self.assertRaises(KeyError):
            self.left.join(self.right, 'one', 'seven')

    def test_inner_join(self):
        new_table = self.left.join(self.right, 'one', 'four', inner=True)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 4, 'a'),
            (2, 3, 'b', 3, 'b'),
            (None, 2, 'c', 2, 'c')
        ])

    def test_inner_join2(self):
        new_table = self.left.join(self.right, 'one', 'five', inner=True)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (2, 3, 'b', None, 'c')
        ])

    def test_inner_join_same_column_name(self):
        right_column_names = ['four', 'one', 'six']

        right = Table(self.right_rows, right_column_names, self.column_types)

        new_table = self.left.join(right, 'one', inner=True)

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Text])
        self.assertRows(new_table, [
            (2, 3, 'b', None, 'c')
        ])

    def test_inner_join_func(self):
        new_table = self.left.join(
            self.right,
            lambda left: '%i%s' % (left['two'], left['three']),
            lambda right: '%i%s' % (right['five'], right['six']),
            inner=True
        )

        self.assertIsNot(new_table, self.left)
        self.assertIsNot(new_table, self.right)
        self.assertColumnNames(new_table, ['one', 'two', 'three', 'four', 'five', 'six'])
        self.assertColumnTypes(new_table, [Number, Number, Text, Number, Number, Text])
        self.assertRows(new_table, [
            (1, 4, 'a', 1, 4, 'a')
        ])

    def test_join_with_row_names(self):
        left = Table(self.left_rows, self.left_column_names, self.column_types, row_names='three')
        new_table = left.join(self.right, 'one', 'four')

        self.assertRowNames(new_table, ('a', 'b', 'c'))

class TestMerge(AgateTestCase):
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

        self.assertIsNot(table_c, table_a)
        self.assertIsNot(table_c, table_b)
        self.assertColumnNames(table_c, self.column_names)
        self.assertColumnTypes(table_c, [Number, Number, Text])
        self.assertRows(table_c, self.rows + self.rows)

    def test_merge_different_names(self):
        table_a = Table(self.rows, self.column_names, self.column_types)

        column_names = ['a', 'b', 'c']

        table_b = Table(self.rows, column_names, self.column_types)
        table_c = Table.merge([table_a, table_b])

        self.assertIsNot(table_c, table_a)
        self.assertIsNot(table_c, table_b)
        self.assertColumnNames(table_c, self.column_names)
        self.assertColumnTypes(table_c, [Number, Number, Text])
        self.assertRows(table_c, self.rows + self.rows)

        for row in table_c.rows:
            self.assertSequenceEqual(row.keys(), self.column_names)

    def test_merge_different_types(self):
        table_a = Table(self.rows, self.column_names, self.column_types)

        column_types = [self.number_type, self.text_type, self.text_type]

        table_b = Table(self.rows, self.column_names, column_types)

        with self.assertRaises(ValueError):
            table_c = Table.merge([table_a, table_b])

    def test_merge_with_row_names(self):
        table_a = Table(self.rows, self.column_names, self.column_types, row_names='three')

        b_rows = (
            (1, 4, 'd'),
            (2, 3, 'e'),
            (None, 2, 'f')
        )

        table_b = Table(b_rows, self.column_names, self.column_types, row_names='three')
        table_c = Table.merge([table_a, table_b], row_names='three')

        self.assertRowNames(table_c, ['a', 'b', 'c', 'd', 'e', 'f'])

class TestData(AgateTestCase):
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
            ('new2', Formula(self.number_type, lambda r: r['one']))
        ])
        table3 = table2.compute([
            ('new3', Formula(self.number_type, lambda r: r['one']))
        ])

        self.assertIsNot(table.rows[0], table2.rows[0])
        self.assertNotEqual(table.rows[0], table2.rows[0])
        self.assertIsNot(table2.rows[0], table3.rows[0])
        self.assertNotEqual(table2.rows[0], table3.rows[0])
        self.assertSequenceEqual(table.rows[0], (1, 4, 'a'))

    def test_rename_row_names(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(row_names=['a','b','c'])

        self.assertSequenceEqual(table2.row_names, ['a','b','c'])
        self.assertSequenceEqual(table2.column_names, self.column_names)

        self.assertIs(table.row_names, None)
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_row_names_dict(self):
        table = Table(self.rows, self.column_names, self.column_types, row_names=['a', 'b', 'c'])
        table2 = table.rename(row_names={'b': 'd'})

        self.assertSequenceEqual(table2.row_names, ['a', 'd', 'c'])
        self.assertSequenceEqual(table2.column_names, self.column_names)

        self.assertSequenceEqual(table.row_names, ['a', 'b', 'c'])
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_column_names(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(column_names=['d','e','f'])

        self.assertIs(table2.row_names, None)
        self.assertSequenceEqual(table2.column_names, ['d','e','f'])

        self.assertIs(table.row_names, None)
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_column_names_dict(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(column_names={'two': 'second'})

        self.assertIs(table2.row_names, None)
        self.assertSequenceEqual(table2.column_names, ['one','second','three'])

        self.assertIs(table.row_names, None)
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_column_names_renames_row_values(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_column_names = ['d', 'e', 'f']
        table2 = table.rename(column_names=new_column_names)

        self.assertColumnNames(table2, new_column_names)


class TableHTMLParser(html_parser.HTMLParser):
    """
    Parser for use in testing HTML rendering of tables.
    """
    def __init__(self, *args, **kwargs):
        html_parser.HTMLParser.__init__(self, *args, **kwargs)

        self.has_table = False
        self.has_thead = False
        self.has_tbody = False
        self.header_rows = []
        self.body_rows = []
        self._in_table = False
        self._in_thead = False
        self._in_tbody = False
        self._in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self._in_table = True
            return

        if tag == 'thead':
            self._in_thead = True
            return

        if tag == 'tbody':
            self._in_tbody = True
            return

        if tag == 'tr':
            self._current_row = []
            return

        if tag in ('td', 'th'):
            self._in_cell = True
            return

    def handle_endtag(self, tag):
        if tag == 'table':
            if self._in_table:
                self.has_table = True
            self._in_table = False
            return

        if tag == 'thead':
            if self._in_thead:
                self.has_thead = True
            self._in_thead = False
            return

        if tag == 'tbody':
            if self._in_tbody:
                self.has_tbody = True
            self._in_tbody = False
            return

        if tag == 'tr':
            if self._in_tbody:
                self.body_rows.append(self._current_row)
            elif self._in_thead:
                self.header_rows.append(self._current_row)

            return

        if tag in ('td', 'th'):
            self._in_cell = False
            return

    def handle_data(self, data):
        if self._in_cell:
            self._current_row.append(data)
            return

class TestPrintHTML(AgateTestCase):
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

    def test_print_html(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table_html = six.StringIO()
        table.print_html(output=table_html)
        table_html = table_html.getvalue()

        parser = TableHTMLParser()
        parser.feed(table_html)

        self.assertIs(parser.has_table, True)
        self.assertIs(parser.has_tbody, True)
        self.assertIs(parser.has_thead, True)
        self.assertEqual(len(parser.header_rows), 1)
        self.assertEqual(len(parser.body_rows), len(table.rows))

        header_cols = parser.header_rows[0]

        self.assertEqual(len(header_cols), len(table.column_names))

        for i, column_name in enumerate(table.column_names):
            self.assertEqual(header_cols[i], column_name)

        for row_num, row in enumerate(table.rows):
            html_row = parser.body_rows[row_num]

            self.assertEqual(len(html_row), len(row))

            for i, col in enumerate(row):
                self.assertEqual(six.text_type(col), html_row[i])
