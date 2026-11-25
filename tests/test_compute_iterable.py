from agate import Table
from agate.computations import Formula
from agate.data_types import Number
from agate.testcase import AgateTestCase


class TestComputeIterable(AgateTestCase):
    def test_generator_computes_all_new_columns(self):
        table = Table([(2,), (3,)], ['value'], [Number()])
        computations = [
            ('double', Formula(Number(), lambda row: row['value'] * 2)),
            ('next', Formula(Number(), lambda row: row['value'] + 1))
        ]

        result = table.compute(computation for computation in computations)

        self.assertColumnNames(result, ['value', 'double', 'next'])
        self.assertRows(result, [(2, 4, 3), (3, 6, 4)])
        self.assertRows(table, [(2,), (3,)])
        self.assertColumnNames(table, ['value'])

    def test_iterator_replaces_existing_column(self):
        table = Table([(2,), (3,)], ['value'], [Number()])
        computations = iter([('value', Formula(Number(), lambda row: row['value'] * 2))])

        result = table.compute(computations, replace=True)

        self.assertColumnNames(result, ['value'])
        self.assertRows(result, [(4,), (6,)])
        self.assertRows(table, [(2,), (3,)])

    def test_empty_iterator_preserves_rows(self):
        table = Table([(2,)], ['value'], [Number()])

        result = table.compute(iter([]))

        self.assertColumnNames(result, ['value'])
        self.assertRows(result, [(2,)])
