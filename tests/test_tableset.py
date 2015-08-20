#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from journalism import Table, TableSet
from journalism.columns import TextType, NumberType

class TestTable(unittest.TestCase):
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

        self.tables = {
            'table1': Table(self.table1, self.column_types, self.column_names),
            'table2': Table(self.table2, self.column_types, self.column_names),
            'table3': Table(self.table3, self.column_types, self.column_names)
        }

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

        new_tableset = tableset.select(['number'])

        for name, new_table in new_tableset.items():
            self.assertEqual(len(new_table.rows), 3)
            self.assertEqual(len(new_table.columns), 1)
            self.assertSequenceEqual(new_table._column_types, (self.number_type,))
            self.assertSequenceEqual(new_table._column_names, ('number',))

    def test_column_any(self):
        tableset = TableSet(self.tables)

        max_lengths = tableset.columns['letter'].any(lambda d: d == 'b')

        self.assertEqual(max_lengths, {
            'table1': True,
            'table2': True,
            'table3': False
        })

    def test_column_max_length(self):
        tableset = TableSet(self.tables)

        max_lengths = tableset.columns['letter'].max_length()

        self.assertEqual(max_lengths, {
            'table1': 1,
            'table2': 1,
            'table3': 1
        })

    def test_column_sum(self):
        tableset = TableSet(self.tables)

        max_lengths = tableset.columns['number'].sum()

        self.assertEqual(max_lengths, {
            'table1': 6,
            'table2': 7,
            'table3': 6
        })
