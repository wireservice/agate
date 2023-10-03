from collections import OrderedDict

from agate import Table, TableSet
from agate.aggregations import Count, Sum
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestHaving(AgateTestCase):
    def setUp(self):
        self.table1 = (
            ('a', 1),
            ('a', 3),
            ('b', 2)
        )

        self.table2 = (
            ('b', 0),
            ('a', 2),
            ('c', 5),
            ('c', 3)
        )

        self.table3 = (
            ('a', 1),
            ('a', 2),
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

    def test_having_simple(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        new_tableset = tableset.having([
            ('count', Count())
        ], lambda t: t['count'] < 3)

        self.assertIsInstance(new_tableset, TableSet)
        self.assertSequenceEqual(new_tableset.keys(), ['table3'])
        self.assertIs(new_tableset.values()[0], tableset['table3'])
        self.assertEqual(new_tableset.key_name, 'test')

    def test_having_complex(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        new_tableset = tableset.having([
            ('count', Count()),
            ('number_sum', Sum('number'))
        ], lambda t: t['count'] >= 3 and t['number_sum'] > 6)

        self.assertIsInstance(new_tableset, TableSet)
        self.assertSequenceEqual(new_tableset.keys(), ['table2'])
        self.assertIs(new_tableset.values()[0], tableset['table2'])
        self.assertEqual(new_tableset.key_name, 'test')
