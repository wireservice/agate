from collections import OrderedDict

from agate import Table, TableSet
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestAggregate(AgateTestCase):
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
            tableset.merge(groups=['red', 'blue'], group_name='color_code')

    def test_merge_groups_invalid_type(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        with self.assertRaises(ValueError):
            tableset.merge(groups='invalid', group_name='color_code')
