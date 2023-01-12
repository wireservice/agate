# !/usr/bin/env python

from io import StringIO

from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestPrintStructure(AgateTestCase):
    def setUp(self):
        self.rows = (
            ('1.7', 2000, 'a'),
            ('11.18', None, None),
            ('0', 1, 'c')
        )

        self.number_type = Number()
        self.international_number_type = Number(locale='de_DE.UTF-8')
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [
            self.number_type,
            self.international_number_type,
            self.text_type
        ]

    def test_print_structure(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.print_structure(output=output)
        lines = output.getvalue().strip().split('\n')

        self.assertEqual(len(lines), 5)
