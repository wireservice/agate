from collections import OrderedDict

import leather

from agate import Table, TableSet
from agate.data_types import Number, Text


class TestTableSetCharts(leather.LeatherTestCase):
    def setUp(self):
        self.table1 = (
            ('a', 1, 4),
            ('b', 3, 7),
            ('c', 2, 2)
        )

        self.table2 = (
            ('a', 0, 3),
            ('b', 2, 3),
            ('c', 5, 3)
        )

        self.table3 = (
            ('a', 1, 10),
            ('b', 2, 1),
            ('c', 3, None)
        )

        self.text_type = Text()
        self.number_type = Number()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.text_type, self.number_type, self.number_type]

        self.tables = OrderedDict([
            ('table1', Table(self.table1, self.column_names, self.column_types)),
            ('table2', Table(self.table2, self.column_names, self.column_types)),
            ('table3', Table(self.table3, self.column_names, self.column_types))
        ])

        self.tablesets = TableSet(self.tables.values(), self.tables.keys())

    def test_bar_chart(self):
        text = self.tablesets.bar_chart(label='one', value='three')
        svg = self.parse_svg(text)

        self.assertElementCount(svg, '.axis', 6)
        self.assertElementCount(svg, '.series', 3)
        self.assertElementCount(svg, '.bars', 3)
        self.assertElementCount(svg, '.bars rect', 8)

        text2 = self.tablesets.bar_chart(label=0, value=2)
        self.assertEqual(text, text2)

    def test_column_chart(self):
        text = self.tablesets.column_chart(label='one', value='three')
        svg = self.parse_svg(text)

        self.assertElementCount(svg, '.axis', 6)
        self.assertElementCount(svg, '.series', 3)
        self.assertElementCount(svg, '.columns', 3)
        self.assertElementCount(svg, '.columns rect', 8)

        text2 = self.tablesets.column_chart(label=0, value=2)
        self.assertEqual(text, text2)

    def test_line_chart(self):
        text = self.tablesets.line_chart(x='two', y='three')
        svg = self.parse_svg(text)

        self.assertElementCount(svg, '.axis', 6)
        self.assertElementCount(svg, '.series', 3)
        self.assertElementCount(svg, 'path', 3)

        text2 = self.tablesets.line_chart(x=1, y=2)
        self.assertEqual(text, text2)

    def test_scatterplot(self):
        text = self.tablesets.scatterplot(x='two', y='three')
        svg = self.parse_svg(text)

        self.assertElementCount(svg, '.axis', 6)
        self.assertElementCount(svg, '.series', 3)
        self.assertElementCount(svg, '.dots', 3)
        self.assertElementCount(svg, 'circle', 8)

        text2 = self.tablesets.scatterplot(x=1, y=2)
        self.assertEqual(text, text2)
