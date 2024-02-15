import leather

from agate import Table
from agate.data_types import Number, Text


class TestTableCharts(leather.LeatherTestCase):
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

    def test_bar_chart(self):
        text = self.table.bar_chart(label='three', value='one')
        svg = self.parse_svg(text)

        self.assertElementCount(svg, '.axis', 2)
        self.assertElementCount(svg, '.series', 1)
        self.assertElementCount(svg, '.bars', 1)
        self.assertElementCount(svg, 'rect', 3)

        text2 = self.table.bar_chart(label=2, value=0)

        self.assertEqual(text, text2)

    def test_column_chart(self):
        text = self.table.column_chart(label='three', value='one')
        svg = self.parse_svg(text)

        self.assertElementCount(svg, '.axis', 2)
        self.assertElementCount(svg, '.series', 1)
        self.assertElementCount(svg, '.columns', 1)
        self.assertElementCount(svg, 'rect', 3)

        text2 = self.table.column_chart(label=2, value=0)

        self.assertEqual(text, text2)

    def test_line_chart(self):
        text = self.table.line_chart(x='one', y='two')
        svg = self.parse_svg(text)

        self.assertElementCount(svg, '.axis', 2)
        self.assertElementCount(svg, '.series', 1)
        self.assertElementCount(svg, 'path', 1)

        text2 = self.table.line_chart(x=0, y=1)

        self.assertEqual(text, text2)

    def test_scatterplot(self):
        text = self.table.scatterplot(x='one', y='two')
        svg = self.parse_svg(text)

        self.assertElementCount(svg, '.axis', 2)
        self.assertElementCount(svg, '.series', 1)
        self.assertElementCount(svg, '.dots', 1)
        self.assertElementCount(svg, 'circle', 2)

        text2 = self.table.scatterplot(x=0, y=1)

        self.assertEqual(text, text2)
