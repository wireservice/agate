from collections import OrderedDict
from decimal import Decimal

from agate import Table, TableSet
from agate.aggregations import Count, MaxLength, Mean, Min, Sum
from agate.data_types import Number, Text
from agate.exceptions import DataTypeError
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

    def test_aggregate_key_name(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        new_table = tableset.aggregate([
            ('count', Count())
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
            ('count', Count())
        ])

        self.assertIsInstance(new_table, Table)
        self.assertColumnNames(new_table, ('test', 'count'))
        self.assertColumnTypes(new_table, [Number, Number])

    def test_aggregate_row_names(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        new_table = tableset.aggregate([
            ('count', Count())
        ])

        self.assertRowNames(new_table, ['table1', 'table2', 'table3'])

    def test_aggregate_sum(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_table = tableset.aggregate([
            ('count', Count()),
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
            ('count', Count()),
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
            ('count', Count()),
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
            ('count', Count()),
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

    def test_nested_aggregation(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        nested = tableset.group_by('letter')

        results = nested.aggregate([
            ('count', Count()),
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
            ('count', Count()),
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
