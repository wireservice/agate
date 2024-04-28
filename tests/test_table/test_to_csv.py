import csv
import os
import sys
from io import StringIO

from agate import Table
from agate.data_types import Boolean, Date, DateTime, Number, Text, TimeDelta
from agate.testcase import AgateTestCase


class TestToCSV(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 'a', True, '11/4/2015', '11/4/2015 12:22 PM', '4:15'),
            (2, '👍', False, '11/5/2015', '11/4/2015 12:45 PM', '6:18'),
            (None, 'b', None, None, None, None)
        )

        self.column_names = [
            'number', 'text', 'boolean', 'date', 'datetime', 'timedelta'
        ]

        self.column_types = [
            Number(), Text(), Boolean(), Date(), DateTime(), TimeDelta()
        ]

    def test_to_csv_quote_nonnumeric(self):
        table = Table(self.rows, self.column_names, self.column_types)

        table.to_csv('.test.csv', quoting=csv.QUOTE_NONNUMERIC)

        with open('.test.csv') as f:
            contents1 = f.read()

        with open('examples/test_quote_nonnumeric.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

        os.remove('.test.csv')

    def test_to_csv(self):
        table = Table(self.rows, self.column_names, self.column_types)

        table.to_csv('.test.csv')

        with open('.test.csv') as f:
            contents1 = f.read()

        with open('examples/test.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

        os.remove('.test.csv')

    def test_to_csv_file_like_object(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with open('.test.csv', 'w') as f:
            table.to_csv(f)

            # Should leave the file open
            self.assertFalse(f.closed)

        with open('.test.csv') as f:
            contents1 = f.read()

        with open('examples/test.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

        os.remove('.test.csv')

    def test_to_csv_to_stdout(self):
        table = Table(self.rows, self.column_names, self.column_types)

        output = StringIO()
        table.to_csv(output)

        contents1 = output.getvalue()

        with open('examples/test.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

    def test_to_csv_make_dir(self):
        table = Table(self.rows, self.column_names, self.column_types)

        table.to_csv('newdir/test.csv')

        with open('newdir/test.csv') as f:
            contents1 = f.read()

        with open('examples/test.csv') as f:
            contents2 = f.read()

        self.assertEqual(contents1, contents2)

        os.remove('newdir/test.csv')
        os.rmdir('newdir/')

    def test_print_csv(self):
        table = Table(self.rows, self.column_names, self.column_types)

        old = sys.stdout
        sys.stdout = StringIO()

        try:
            table.print_csv()

            contents1 = sys.stdout.getvalue()

            with open('examples/test.csv') as f:
                contents2 = f.read()

            self.assertEqual(contents1, contents2)
        finally:
            sys.stdout = old
