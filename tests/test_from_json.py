from agate import Table
from agate.data_types import Boolean, Date, DateTime, Number, Text, TimeDelta
from agate.rows import Row
from agate.testcase import AgateTestCase
from agate.type_tester import TypeTester


class TestJSON(AgateTestCase):
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

    def test_from_json(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_json('examples/test.json')

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])
        self.assertRows(table2, table1.rows)

    def test_from_json_file_like_object(self):
        table1 = Table(self.rows, self.column_names, self.column_types)

        with open('examples/test.json', encoding='utf-8') as f:
            table2 = Table.from_json(f)

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])
        self.assertRows(table2, table1.rows)

    def test_from_json_with_key(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_json('examples/test_key.json', key='data')

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])
        self.assertRows(table2, table1.rows)

    def test_from_json_mixed_keys(self):
        table = Table.from_json('examples/test_mixed.json')

        self.assertColumnNames(table, ['one', 'two', 'three', 'four', 'five'])
        self.assertColumnTypes(table, [Number, Number, Text, Text, Number])
        self.assertRows(table, [
            [1, 4, 'a', None, None],
            [2, 3, 'b', 'd', None],
            [None, 2, '👍', None, 5]
        ])

    def test_from_json_nested(self):
        table = Table.from_json('examples/test_nested.json')

        self.assertColumnNames(table, ['one', 'two/two_a', 'two/two_b', 'three/0', 'three/1', 'three/2'])
        self.assertColumnTypes(table, [Number, Text, Text, Text, Number, Text])
        self.assertRows(table, [
            [1, 'a', 'b', 'a', 2, 'c'],
            [2, 'c', 'd', 'd', 2, 'f']
        ])

    def test_from_json_newline_delimited(self):
        table1 = Table(self.rows, self.column_names, self.column_types)
        table2 = Table.from_json('examples/test_newline.json', newline=True)

        self.assertColumnNames(table2, self.column_names)
        self.assertColumnTypes(table2, [Number, Text, Boolean, Date, DateTime, TimeDelta])
        self.assertRows(table2, table1.rows)

    def test_from_json_no_type_tester(self):
        tester = TypeTester(limit=0)

        table = Table.from_json('examples/test.json', column_types=tester)

        self.assertColumnTypes(table, [Text, Text, Text, Text, Text, Text])

    def test_from_json_error_newline_key(self):
        with self.assertRaises(ValueError):
            Table.from_json('examples/test.json', newline=True, key='test')

    def test_from_json_ambiguous(self):
        table = Table.from_json('examples/test_from_json_ambiguous.json')

        self.assertColumnNames(table, ('a/b',))
        self.assertColumnTypes(table, [Boolean])
        self.assertRows(table, [Row([False])])
