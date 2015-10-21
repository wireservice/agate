#!/usr/bin/env python
# -*- coding: utf8 -*-

import pickle

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate import Table
from agate.aggregations import HasNulls
from agate.data_types import *

class TestColumn(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.columns = (
            ('one', self.number_type),
            ('two', self.number_type),
            ('three', self.text_type)
        )

        self.table = Table(self.rows, self.columns)

    def test_name(self):
        self.assertEqual(self.table.columns['one'].name, 'one')

    def test_data_type(self):
        self.assertIs(self.table.columns['one'].data_type, self.number_type)

    def test_pickleable(self):
        pickle.dumps(self.table.columns['one'])

    def test_row_names(self):
        table = Table(self.rows, self.columns, row_names='three')
        column = table.columns['one']

        self.assertSequenceEqual(column._row_names, ['a', 'b', 'c'])
        self.assertEqual(column['b'], 2)

    def test_keys(self):
        table = Table(self.rows, self.columns, row_names='three')

        self.assertIs(self.table.columns['one'].keys(), None)
        self.assertSequenceEqual(table.columns['one'].keys(), ['a', 'b', 'c'])

    def test_values(self):
        self.assertSequenceEqual(
            self.table.columns['one'].values(),
            [Decimal('1'), Decimal('2'), None]
        )

    def test_items(self):
        table = Table(self.rows, self.columns, row_names='three')

        self.assertSequenceEqual(table.columns['one'].items(), [
            ('a', Decimal('1')),
            ('b', Decimal('2')),
            ('c', None)
        ])

    def test_dict(self):
        table = Table(self.rows, self.columns, row_names='three')

        self.assertDictEqual(table.columns['one'].dict(), {
            'a': Decimal('1'),
            'b': Decimal('2'),
            'c': None
        })

    def test_values_without_nulls(self):
        self.assertSequenceEqual(
            self.table.columns['one'].values_without_nulls(),
            [Decimal('1'), Decimal('2')]
        )

    def test_values_sorted(self):
        rows = (
            (2, 2, 'a'),
            (None, 3, 'b'),
            (1, 4, 'c')
        )

        table = Table(rows, self.columns)

        self.assertSequenceEqual(
            table.columns['one'].values_sorted(),
            [Decimal('1'), Decimal('2'), None]
        )

    def test_values_without_nulls_sorted(self):
        rows = (
            (2, 2, 'a'),
            (None, 3, 'b'),
            (1, 4, 'c')
        )

        table = Table(rows, self.columns)

        self.assertSequenceEqual(
            table.columns['one'].values_without_nulls_sorted(),
            [Decimal('1'), Decimal('2')]
        )

    def test_aggregate(self):
        self.assertTrue(self.table.columns['one'].aggregate(HasNulls()))
        self.assertFalse(self.table.columns['two'].aggregate(HasNulls()))
