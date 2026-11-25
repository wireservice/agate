import datetime

from agate import Table, TypeTester
from agate.data_types import Date, Number, Text
from agate.testcase import AgateTestCase


class TestTypeTesterZeroForce(AgateTestCase):
    def test_zero_limit_retains_forced_type_instances(self):
        number = Number()
        date = Date(date_format='%Y-%m-%d')
        tester = TypeTester(limit=0, force={'number': number, 'date': date})

        types = tester.run([['2', '2020-01-02', '3']], ['number', 'date', 'text'])

        self.assertIs(types[0], number)
        self.assertIs(types[1], date)
        self.assertIsInstance(types[2], Text)

    def test_table_casts_forced_columns_without_inference(self):
        tester = TypeTester(limit=0, force={'number': Number(), 'date': Date(date_format='%Y-%m-%d')})

        table = Table([['2', '2020-01-02', '3']], ['number', 'date', 'text'], tester)

        self.assertColumnTypes(table, [Number, Date, Text])
        self.assertRows(table, [(2, datetime.date(2020, 1, 2), '3')])

    def test_zero_limit_without_overrides_still_uses_text(self):
        table = Table([['2', 'true']], ['number', 'boolean'], TypeTester(limit=0))

        self.assertColumnTypes(table, [Text, Text])
        self.assertRows(table, [('2', 'true')])
