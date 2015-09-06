#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate.column_types import *
from agate.inference import TypeTester
from agate.table import Table

class TestTypeInference(unittest.TestCase):
    def setUp(self):
        self.tester = TypeTester()

    def test_text_type(self):
        rows = [
            ('a',),
            ('b',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0][1], TextType)

    def test_number_type(self):
        rows = [
            ('1.7',),
            ('200000000',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0][1], NumberType)

    def test_boolean_type(self):
        rows = [
            ('True',),
            ('FALSE',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0][1], BooleanType)

    def test_date_time_type(self):
        rows = [
            ('5/7/84 3:44:12',),
            ('2/28/1997 3:12 AM',),
            ('3/19/20',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0][1], DateTimeType)

    def test_time_delta_type(self):
        rows = [
            ('1:42',),
            ('1w 27h',),
            ('',)
        ]

        inferred = self.tester.run(rows, ['one'])

        self.assertIsInstance(inferred[0][1], TimeDeltaType)

    def test_from_csv(self):
        table = Table.from_csv('examples/test.csv', self.tester)

        self.assertSequenceEqual(table.get_column_names(), ['one', 'two', 'three'])
        self.assertSequenceEqual(map(type, table.get_column_types()), [NumberType, NumberType, TextType])

        self.assertEqual(len(table.columns), 3)

        self.assertSequenceEqual(table.rows[0], [1, 4, 'a'])
        self.assertSequenceEqual(table.rows[1], [2, 3, 'b'])
        self.assertSequenceEqual(table.rows[2], [None, 2, 'c'])
