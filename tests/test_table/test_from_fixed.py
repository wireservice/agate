from agate import Table
from agate.testcase import AgateTestCase


class TestFromFixed(AgateTestCase):
    def test_from_fixed(self):
        table1 = Table.from_csv('examples/testfixed_converted.csv')
        table2 = Table.from_fixed('examples/testfixed', 'examples/testfixed_schema.csv')

        self.assertColumnNames(table2, table1.column_names)
        self.assertColumnTypes(table2, [type(c) for c in table1.column_types])

        self.assertRows(table2, table1.rows)
