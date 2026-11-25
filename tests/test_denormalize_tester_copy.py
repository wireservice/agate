from agate import Table, TypeTester
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestDenormalizeTesterCopy(AgateTestCase):
    def test_supplied_tester_is_not_modified(self):
        tester = TypeTester()
        table = Table([('a', 'amount', 2)], ['id', 'property', 'value'], [Text(), Text(), Number()])

        result = table.denormalize(['id'], column_types=tester)

        self.assertRows(result, [('a', 2)])
        self.assertEqual(tester._force, {})

    def test_reusing_tester_does_not_carry_key_types_between_tables(self):
        tester = TypeTester()
        text_table = Table([('a', 'amount', 2)], ['id', 'property', 'value'], [Text(), Text(), Number()])
        number_table = Table([(3, 'amount', 4)], ['id', 'property', 'value'], [Number(), Text(), Number()])

        text_table.denormalize(['id'], column_types=tester)
        result = number_table.denormalize(['id'], column_types=tester)

        self.assertColumnTypes(result, [Number, Number])
        self.assertRows(result, [(3, 4)])

    def test_explicit_forced_type_takes_precedence(self):
        forced = Text()
        overrides = {'id': forced}
        tester = TypeTester(force=overrides)
        table = Table([(3, 'amount', 4)], ['id', 'property', 'value'], [Number(), Text(), Number()])

        result = table.denormalize(['id'], column_types=tester)

        self.assertIs(result.column_types[0], forced)
        self.assertRows(result, [('3', 4)])
        self.assertIs(tester._force, overrides)
