import warnings
from html.parser import HTMLParser
from io import StringIO

from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TableHTMLParser(HTMLParser):
    """
    Parser for use in testing HTML rendering of tables.
    """

    def __init__(self):
        warnings.simplefilter('ignore')

        try:
            HTMLParser.__init__(self)
        finally:
            warnings.resetwarnings()

        self.has_table = False
        self.has_thead = False
        self.has_tbody = False
        self.header_rows = []
        self.body_rows = []
        self._in_table = False
        self._in_thead = False
        self._in_tbody = False
        self._in_cell = False
        self._cell_data = None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self._in_table = True
            return

        if tag == 'thead':
            self._in_thead = True
            return

        if tag == 'tbody':
            self._in_tbody = True
            return

        if tag == 'tr':
            self._current_row = []
            return

        if tag in ('td', 'th'):
            self._in_cell = True
            return

    def handle_endtag(self, tag):
        if tag == 'table':
            if self._in_table:
                self.has_table = True
            self._in_table = False
            return

        if tag == 'thead':
            if self._in_thead:
                self.has_thead = True
            self._in_thead = False
            return

        if tag == 'tbody':
            if self._in_tbody:
                self.has_tbody = True
            self._in_tbody = False
            return

        if tag == 'tr':
            if self._in_tbody:
                self.body_rows.append(self._current_row)
            elif self._in_thead:
                self.header_rows.append(self._current_row)

            return

        if tag in ('td', 'th'):
            self._current_row.append(self._cell_data)
            self._cell_data = None
            self._in_cell = False
            return

    def handle_data(self, data):
        if self._in_cell:
            self._cell_data = data
            return


class TestPrintHTML(AgateTestCase):
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

    def test_print_html(self):
        table = Table(self.rows, self.column_names, self.column_types)
        table_html = StringIO()
        table.print_html(output=table_html)
        table_html = table_html.getvalue()

        parser = TableHTMLParser()
        parser.feed(table_html)

        self.assertIs(parser.has_table, True)
        self.assertIs(parser.has_tbody, True)
        self.assertIs(parser.has_thead, True)
        self.assertEqual(len(parser.header_rows), 1)
        self.assertEqual(len(parser.body_rows), len(table.rows))

        header_cols = parser.header_rows[0]

        self.assertEqual(len(header_cols), len(table.column_names))

        for i, column_name in enumerate(table.column_names):
            self.assertEqual(header_cols[i], column_name)

        for row_num, row in enumerate(table.rows):
            html_row = parser.body_rows[row_num]

            self.assertEqual(len(html_row), len(row))

    def test_print_html_tags(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.print_html(output=output)
        html = output.getvalue()

        self.assertEqual(html.count('<tr>'), 4)
        self.assertEqual(html.count('<th>'), 3)
        self.assertEqual(html.count('<td '), 9)

    def test_print_html_max_rows(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.print_html(max_rows=2, output=output)
        html = output.getvalue()

        self.assertEqual(html.count('<tr>'), 4)
        self.assertEqual(html.count('<th>'), 3)
        self.assertEqual(html.count('<td '), 9)

    def test_print_html_max_columns(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.print_html(max_columns=2, output=output)
        html = output.getvalue()

        self.assertEqual(html.count('<tr>'), 4)
        self.assertEqual(html.count('<th>'), 3)
        self.assertEqual(html.count('<td '), 9)
