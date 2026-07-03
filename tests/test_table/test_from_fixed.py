from agate import Table
from agate.testcase import AgateTestCase


class TestFromFixed(AgateTestCase):
    def test_from_fixed(self):
        table1 = Table.from_csv('examples/testfixed_converted.csv')
        table2 = Table.from_fixed('examples/testfixed', 'examples/testfixed_schema.csv')

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [type(c) for c in table1.column_types])

        self.assertRows(table2, table1.rows)

    def test_from_fixed_file_like_objects(self):
        table1 = Table.from_csv('examples/testfixed_converted.csv')

        with open('examples/testfixed', encoding='utf-8') as f, \
                open('examples/testfixed_schema.csv', encoding='utf-8') as schema_f:
            table2 = Table.from_fixed(f, schema_f)

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [type(c) for c in table1.column_types])

        self.assertRows(table2, table1.rows)
