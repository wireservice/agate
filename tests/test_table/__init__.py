#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

import io
import json
import warnings

import os
import sys

import six

from agate import Table
from agate.data_types import *
from agate.computations import Formula
from agate.testcase import AgateTestCase
from agate.type_tester import TypeTester
from agate.warns import DuplicateColumnWarning


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

        print(table.rows)
        print(table.columns)

        self.assertColumnNames(table, ['a', 'b', 'c'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_filename(self):
        with self.assertRaises(ValueError):
            table = Table('foo.csv')  # noqa

    def test_create_empty_table(self):
        table = Table([])
        table2 = Table([], self.column_names, self.column_types)

        self.assertColumnNames(table, [])
        self.assertColumnTypes(table, [])
        self.assertRows(table, [])

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Number, Text])
        self.assertRows(table2, [])

    def test_create_table_column_types(self):
        column_types = [self.number_type, self.text_type, self.text_type]
        table = Table(self.rows, column_types=column_types)

        self.assertColumnNames(table, ['a', 'b', 'c'])
        self.assertColumnTypes(table, [Number, Text, Text])
        self.assertRows(table, [
            (1, '4', 'a'),
            (2, '3', 'b'),
            (None, '2', u'👍')
        ])

    def test_create_table_column_types_dict(self):
        column_types = dict(zip(self.column_names, self.column_types))
        table = Table(self.rows, column_names=self.column_names, column_types=column_types)

        self.assertColumnNames(table, ['one', 'two', 'three'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

    def test_create_table_partial_column_types_dict(self):
        column_types = dict(zip(self.column_names[:2], self.column_types[:2]))
        table = Table(self.rows, column_names=self.column_names, column_types=column_types)

        self.assertColumnNames(table, ['one', 'two', 'three'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

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

    def test_create_table_null_column_names(self):
        column_names = ['one', None, 'three']

        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(RuntimeWarning):
                table1 = Table(self.rows, column_types=self.column_types)  # noqa

            with self.assertRaises(RuntimeWarning):
                table2 = Table(self.rows, column_names, self.column_types)  # noqa

        table3 = Table(self.rows, column_names, self.column_types)

        self.assertColumnNames(table3, ['one', 'b', 'three'])

    def test_create_table_non_datatype_columns(self):
        column_types = [self.number_type, self.number_type, 'foo']

        with self.assertRaises(ValueError):
            Table(self.rows, self.column_names, column_types)

    def test_create_duplicate_column_names(self):
        column_names = ['one', 'two', 'two']

        warnings.simplefilter('error')

        with self.assertRaises(DuplicateColumnWarning):
            table = Table(self.rows, column_names, self.column_types)

        warnings.simplefilter('ignore')

        table = Table(self.rows, column_names, self.column_types)

        self.assertColumnNames(table, ['one', 'two', 'two_2'])
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, self.rows)

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
        table2 = Table(rows)

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Number, Text])
        self.assertRows(table, [
            (1, 4, 'a'),
            (2, None, None),
            (None, 2, None)
        ])

        self.assertColumnTypes(table2, [Number, Number, Text])
        self.assertRows(table2, [
            (1, 4, 'a'),
            (2, None, None),
            (None, 2, None)
        ])

    def test_create_table_no_column_names(self):
        table = Table(self.rows, None, self.column_types)

        self.assertEqual(len(table.rows), 3)
        self.assertEqual(len(table.columns), 3)

        self.assertSequenceEqual(table.columns[0], (1, 2, None))
        self.assertSequenceEqual(table.columns['a'], (1, 2, None))

        with self.assertRaises(KeyError):
            table.columns[None]

        with self.assertRaises(KeyError):
            table.columns['one']

        self.assertSequenceEqual(table.columns[2], ('a', 'b', u'👍'))
        self.assertSequenceEqual(table.columns['c'], ('a', 'b', u'👍'))

        with self.assertRaises(KeyError):
            table.columns['']

    def test_row_too_long(self):
        rows = (
            (1, 4, 'a', 'foo'),
            (2,),
            (None, 2)
        )

        with self.assertRaises(ValueError):
            table = Table(rows, self.column_names, self.column_types)  # noqa

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
            table = Table(  # noqa
                self.rows,
                self.column_names,
                self.column_types,
                row_names={'a': 1, 'b': 2, 'c': 3}
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

        self.assertColumnNames(table, ['a', 'b', 'c'])
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

        new_table = table.select(('two', 'three'))

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, ['two', 'three'])
        self.assertColumnTypes(new_table, [Number, Text])
        self.assertRows(new_table, [
            [4, 'a'],
            [3, 'b'],
            [2, u'👍']
        ])

    def test_select_single(self):
        table = Table(self.rows, self.column_names, self.column_types)
        new_table = table.select('three')

        self.assertColumnNames(new_table, ['three'])
        self.assertColumnTypes(new_table, [Text])
        self.assertRows(new_table, [
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
        self.assertRows(new_table, [
            ['a'],
            ['b'],
            [u'👍']
        ])

    def test_exclude_single(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_table = table.exclude('one')

        self.assertIsNot(new_table, table)

        self.assertColumnNames(new_table, ['two', 'three'])
        self.assertColumnTypes(new_table, [Number, Text])
        self.assertRows(new_table, [
            [4, 'a'],
            [3, 'b'],
            [2, u'👍']
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
        self.assertRows(new_table, [
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
        self.assertRows(new_table, [
            self.rows[2],
            self.rows[1],
            self.rows[0]
        ])

        # Verify old table not changed
        self.assertRows(table, self.rows)

    def test_order_by_multiple_columns(self):
        rows = (
            (1, 2, 'a'),
            (2, 1, 'b'),
            (1, 1, 'c')
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.order_by(['one', 'two'])

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[2],
            rows[0],
            rows[1]
        ])

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
        self.assertRows(new_table, [
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
        self.assertRows(new_table, [
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

    def test_order_by_empty_table(self):
        table = Table([], self.column_names)

        new_table = table.order_by('three')  # noqa

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

    def test_distinct_multiple_columns(self):
        rows = (
            (1, 2, 'a'),
            (2, None, None),
            (1, 1, 'c'),
            (1, None, None)
        )

        table = Table(rows, self.column_names, self.column_types)

        new_table = table.distinct(['two', 'three'])

        self.assertIsNot(new_table, table)
        self.assertColumnNames(new_table, self.column_names)
        self.assertColumnTypes(new_table, [Number, Number, Text])
        self.assertRows(new_table, [
            rows[0],
            rows[1],
            rows[2]
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

        with io.open('examples/test.csv', encoding='utf-8') as f:
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

    def test_from_csv_no_type_tester(self):
        tester = TypeTester(limit=0)

        table = Table.from_csv('examples/test.csv', column_types=tester)

        self.assertColumnTypes(table, [Text, Text, Text, Text, Text, Text])

    def test_from_csv_no_header(self):
        table = Table.from_csv('examples/test_no_header.csv', header=False)

        self.assertColumnNames(table, ['a', 'b', 'c', 'd', 'e', 'f'])
        self.assertColumnTypes(table, [Number, Text, Boolean, Date, DateTime, TimeDelta])

    def test_from_csv_no_header_columns(self):
        table = Table.from_csv('examples/test_no_header.csv', self.column_names, header=False)

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Text, Boolean, Date, DateTime, TimeDelta])

    def test_from_csv_sniff_limit(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test_csv_sniff.csv', sniff_limit=None)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_skip_lines(self):
        table1 = Table(self.rows[1:], column_types=self.column_types)
        table2 = Table.from_csv('examples/test.csv', header=False, skip_lines=2)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_skip_lines_sequence(self):
        table1 = Table([self.rows[1]], column_names=self.column_names, column_types=self.column_types)
        table2 = Table.from_csv('examples/test.csv', skip_lines=(1, 3))

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

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

        output = six.StringIO()
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
        sys.stdout = six.StringIO()

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

    def test_from_json_no_type_tester(self):
        tester = TypeTester(limit=0)

        table = Table.from_json('examples/test.json', column_types=tester)

        self.assertColumnTypes(table, [Text, Text, Text, Text, Text, Text])

    def test_from_json_error_newline_key(self):
        with self.assertRaises(ValueError):
            table = Table.from_json('examples/test.json', newline=True, key='test')  # noqa

    def test_to_json(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.to_json(output, indent=4)

        js1 = json.loads(output.getvalue())

        with open('examples/test.json') as f:
            js2 = json.load(f)

        self.assertEqual(js1, js2)

    def test_to_json_key(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.to_json(output, key='text', indent=4)

        js1 = json.loads(output.getvalue())

        with open('examples/test_keyed.json') as f:
            js2 = json.load(f)

        self.assertEqual(js1, js2)

    def test_to_json_key_func(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.to_json(output, key=lambda r: r['text'], indent=4)

        js1 = json.loads(output.getvalue())

        with open('examples/test_keyed.json') as f:
            js2 = json.load(f)

        self.assertEqual(js1, js2)

    def test_to_json_newline_delimited(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()
        table.to_json(output, newline=True)

        js1 = json.loads(output.getvalue().split('\n')[0])

        with open('examples/test_newline.json') as f:
            js2 = json.loads(list(f)[0])

        self.assertEqual(js1, js2)

    def test_to_json_error_newline_indent(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()

        with self.assertRaises(ValueError):
            table.to_json(output, newline=True, indent=4)

    def test_to_json_error_newline_key(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = six.StringIO()

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
        sys.stdout = six.StringIO()

        try:
            table.print_json()

            js1 = json.loads(sys.stdout.getvalue())

            with open('examples/test.json') as f:
                js2 = json.load(f)

            self.assertEqual(js1, js2)
        finally:
            sys.stdout = old


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
        table2 = table.rename(row_names=['a', 'b', 'c'])

        self.assertSequenceEqual(table2.row_names, ['a', 'b', 'c'])
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
        table2 = table.rename(column_names=['d', 'e', 'f'])

        self.assertIs(table2.row_names, None)
        self.assertSequenceEqual(table2.column_names, ['d', 'e', 'f'])

        self.assertIs(table.row_names, None)
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_column_names_dict(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table2 = table.rename(column_names={'two': 'second'})

        self.assertIs(table2.row_names, None)
        self.assertSequenceEqual(table2.column_names, ['one', 'second', 'three'])

        self.assertIs(table.row_names, None)
        self.assertSequenceEqual(table.column_names, self.column_names)

    def test_rename_column_names_renames_row_values(self):
        table = Table(self.rows, self.column_names, self.column_types)

        new_column_names = ['d', 'e', 'f']
        table2 = table.rename(column_names=new_column_names)

        self.assertColumnNames(table2, new_column_names)
