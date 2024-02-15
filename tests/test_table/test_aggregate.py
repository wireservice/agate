from agate import Table
from agate.aggregations import Count, Sum
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestAggregate(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 4, 'a'),
            (2, 3, 'b'),
            (None, 2, '👍')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

        self.table = Table(self.rows, self.column_names, self.column_types)

    def test_count(self):
        self.assertEqual(self.table.aggregate(Count()), 3)

    def test_sum(self):
        self.assertEqual(self.table.aggregate(Sum('two')), 9)

    def test_multiple(self):
        self.assertEqual(
            self.table.aggregate([
                ('count', Count()),
                ('sum', Sum('two'))
            ]),
            {
                'count': 3,
                'sum': 9
            }
        )
