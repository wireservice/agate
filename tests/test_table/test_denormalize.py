from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase
from agate.type_tester import TypeTester


class TestDenormalize(AgateTestCase):
    def setUp(self):
        self.rows = (
            ('Jane', 'Code', 'gender', 'female'),
            ('Jane', 'Code', 'age', '27'),
            ('Jim', 'Program', 'gender', 'male'),
            ('Jim', 'Bytes', 'age', '24')
        )

        self.text_type = Text()

        self.column_names = ['first_name', 'last_name', 'property', 'value']
        self.column_types = [self.text_type, self.text_type, self.text_type, self.text_type]

    def test_denormalize(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.denormalize('first_name', 'property', 'value')

        normal_rows = (
            ('Jane', 'female', 27),
            ('Jim', 'male', 24),
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['first_name', 'gender', 'age'])
        self.assertColumnTypes(normalized_table, [Text, Text, Number])
        self.assertRowNames(normalized_table, ['Jane', 'Jim'])

    def test_denormalize_no_key(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.denormalize(None, 'property', 'value')

        # NB: value has been overwritten
        normal_rows = (
            ('male', 24),
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['gender', 'age'])
        self.assertColumnTypes(normalized_table, [Text, Number])

    def test_denormalize_multiple_keys(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.denormalize(['first_name', 'last_name'], 'property', 'value')

        normal_rows = (
            ('Jane', 'Code', 'female', 27),
            ('Jim', 'Program', 'male', None),
            ('Jim', 'Bytes', None, 24),
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['first_name', 'last_name', 'gender', 'age'])
        self.assertColumnTypes(normalized_table, [Text, Text, Text, Number])
        self.assertRowNames(normalized_table, [('Jane', 'Code'), ('Jim', 'Program'), ('Jim', 'Bytes')])

    def test_denormalize_default_value(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.denormalize(['first_name', 'last_name'], 'property', 'value', default_value='hello')

        normal_rows = (
            ('Jane', 'Code', 'female', '27'),
            ('Jim', 'Program', 'male', 'hello'),
            ('Jim', 'Bytes', 'hello', '24'),
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['first_name', 'last_name', 'gender', 'age'])
        self.assertColumnTypes(normalized_table, [Text, Text, Text, Text])

    def test_denormalize_column_types(self):
        table = Table(self.rows, self.column_names, self.column_types)

        normalized_table = table.denormalize(None, 'property', 'value', column_types=[Text(), Number()])

        # NB: value has been overwritten
        normal_rows = (
            ('male', 24),
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['gender', 'age'])
        self.assertColumnTypes(normalized_table, [Text, Number])

    def test_denormalize_column_type_tester(self):
        table = Table(self.rows, self.column_names, self.column_types)

        type_tester = TypeTester(force={'gender': Text()})
        normalized_table = table.denormalize(None, 'property', 'value', column_types=type_tester)

        # NB: value has been overwritten
        normal_rows = (
            ('male', 24),
        )

        self.assertRows(normalized_table, normal_rows)
        self.assertColumnNames(normalized_table, ['gender', 'age'])
        self.assertColumnTypes(normalized_table, [Text, Number])
