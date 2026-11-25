from decimal import Decimal

from agate import Table
from agate.aggregations import First, Sum
from agate.computations import Formula, Percent
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestPivotNoGrouping(AgateTestCase):
    def setUp(self):
        self.table = Table(
            [('001', 2), ('002', 3)], ['label', 'amount'], [Text(), Number()],
            row_names=['first', 'second']
        )

    def test_count(self):
        for key in (None, [], ()):
            with self.subTest(key=key):
                result = self.table.pivot(key=key)
                self.assertColumnNames(result, ['Count'])
                self.assertColumnTypes(result, [Number])
                self.assertEqual(len(result.rows), 1)
                self.assertRows(result, [(Decimal(2),)])
                self.assertIsNone(result.row_names)

    def test_sum(self):
        result = self.table.pivot(aggregation=Sum('amount'))
        self.assertColumnNames(result, ['Sum'])
        self.assertColumnTypes(result, [Number])
        self.assertRows(result, [(Decimal(5),)])

    def test_text_aggregation_preserves_type(self):
        result = self.table.pivot(aggregation=First('label'))
        self.assertColumnNames(result, ['First'])
        self.assertColumnTypes(result, [Text])
        self.assertRows(result, [('001',)])

    def test_computation(self):
        result = self.table.pivot(computation=Percent('Count'))
        self.assertColumnNames(result, ['Percent'])
        self.assertRows(result, [(Decimal(100),)])

    def test_text_computation(self):
        result = self.table.pivot(computation=Formula(Text(), lambda row: 'count=' + str(row['Count'])))
        self.assertColumnNames(result, ['Formula'])
        self.assertColumnTypes(result, [Text])
        self.assertRows(result, [('count=2',)])

    def test_empty_input(self):
        result = self.table.limit(0).pivot()
        self.assertColumnNames(result, ['Count'])
        self.assertColumnTypes(result, [Number])
        self.assertEqual(len(result.rows), 1)
        self.assertRows(result, [(Decimal(0),)])

    def test_aggregation_still_validates(self):
        with self.assertRaises(TypeError):
            self.table.pivot(aggregation=Sum('label'))
