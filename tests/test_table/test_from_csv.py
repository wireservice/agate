import warnings

from agate import Table
from agate.data_types import Boolean, Date, DateTime, Number, Text, TimeDelta
from agate.testcase import AgateTestCase
from agate.type_tester import TypeTester


class TestFromCSV(AgateTestCase):
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

    def test_from_csv(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test.csv')

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_crlf(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test_crlf.csv')

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_cr(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test_cr.csv')

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_file_like_object(self):
        table1 = Table(self.rows, self.column_names, self.column_types)

        f = open('examples/test.csv', encoding='utf-8')

        table2 = Table.from_csv(f)
        f.close()

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_type_tester(self):
        tester = TypeTester(force={
            'number': Text()
        })

        table = Table.from_csv('examples/test.csv', column_types=tester)

        self.assertColumnTypes(table, [Text, Text, Boolean, Date, DateTime, TimeDelta])

    def test_from_csv_no_type_tester(self):
        tester = TypeTester(limit=0)

        table = Table.from_csv('examples/test.csv', column_types=tester)

        self.assertColumnTypes(table, [Text, Text, Text, Text, Text, Text])

    def test_from_csv_no_header(self):
        warnings.simplefilter('ignore')

        try:
            table = Table.from_csv('examples/test_no_header.csv', header=False)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table, ['a', 'b', 'c', 'd', 'e', 'f'])
        self.assertColumnTypes(table, [Number, Text, Boolean, Date, DateTime, TimeDelta])

    def test_from_csv_no_header_columns(self):
        table = Table.from_csv('examples/test_no_header.csv', self.column_names, header=False)

        self.assertColumnNames(table, self.column_names)
        self.assertColumnTypes(table, [Number, Text, Boolean, Date, DateTime, TimeDelta])

    def test_from_csv_sniff_limit_0(self):
        table2 = Table.from_csv('examples/test_csv_sniff.csv', sniff_limit=0)

        self.assertColumnNames(table2, ['number|text|boolean|date|datetime|timedelta'])
        self.assertColumnTypes(table2, [Text])

    def test_from_csv_sniff_limit_200(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test_csv_sniff.csv', sniff_limit=200)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_sniff_limit_none(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test_csv_sniff.csv', sniff_limit=None)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_skip_lines(self):
        warnings.simplefilter('ignore')

        try:
            table1 = Table(self.rows[1:], column_types=self.column_types)
            table2 = Table.from_csv('examples/test.csv', header=False, skip_lines=2)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_skip_lines_crlf(self):
        warnings.simplefilter('ignore')

        try:
            table1 = Table(self.rows[1:], column_types=self.column_types)
            table2 = Table.from_csv('examples/test_crlf.csv', header=False, skip_lines=2)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_skip_lines_cr(self):
        warnings.simplefilter('ignore')

        try:
            table1 = Table(self.rows[1:], column_types=self.column_types)
            table2 = Table.from_csv('examples/test_cr.csv', header=False, skip_lines=2)
        finally:
            warnings.resetwarnings()

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_row_limit(self):
        table1 = Table(self.rows[:2], self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test.csv', row_limit=2)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_row_limit_no_header_columns(self):
        table1 = Table(self.rows[:2], self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test_no_header.csv', self.column_names, header=False, row_limit=2)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_row_limit_too_high(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_csv('examples/test.csv', row_limit=200)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])

        self.assertRows(table2, table1.rows)

    def test_from_csv_empty(self):
        table = Table.from_csv('examples/empty.csv')

        self.assertColumnNames(table, [])
        self.assertColumnTypes(table, [])

        self.assertRows(table, [])
