from collections import OrderedDict

from agate import Table
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestTableSetFindResults(AgateTestCase):
    def test_find_returns_first_row_or_none_for_each_group(self):
        table = Table([('b', 2), ('b', 4), ('a', 1)], ['group', 'value'], [Text(), Number()])
        groups = table.group_by('group')

        result = groups.find(lambda row: row['value'] > 1)

        self.assertIsInstance(result, OrderedDict)
        self.assertEqual(list(result), ['b', 'a'])
        self.assertIs(result['b'], groups['b'].rows[0])
        self.assertIsNone(result['a'])
        self.assertRows(table, [('b', 2), ('b', 4), ('a', 1)])

    def test_find_without_matches(self):
        table = Table([('b', 2), ('a', 1)], ['group', 'value'], [Text(), Number()])

        result = table.group_by('group').find(test=lambda row: False)

        self.assertEqual(result, OrderedDict([('b', None), ('a', None)]))

    def test_nested_groups_return_nested_mappings(self):
        table = Table([('b', 'x', 2), ('b', 'y', 1), ('a', 'x', 3)],
                      ['group', 'kind', 'value'], [Text(), Text(), Number()])
        groups = table.group_by('group').group_by('kind')

        result = groups.find(lambda row: row['value'] > 1)

        self.assertEqual(list(result), ['b', 'a'])
        self.assertIsInstance(result['b'], OrderedDict)
        self.assertEqual(list(result['b']), ['x', 'y'])
        self.assertIs(result['b']['x'], groups['b']['x'].rows[0])
        self.assertIsNone(result['b']['y'])
        self.assertIs(result['a']['x'], groups['a']['x'].rows[0])
