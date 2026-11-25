from agate import Table, utils
from agate.data_types import Number
from agate.testcase import AgateTestCase


class TestObjectKeySlashes(AgateTestCase):
    def test_distinct_edge_slashes_preserve_columns_and_values(self):
        data = {'/amount': 2, 'amount': 3, 'amount/': 4, '/': 5}

        result = Table.from_object([data], column_types=[Number()] * 4)

        self.assertColumnNames(result, ['/amount', 'amount', 'amount/', '/'])
        self.assertRows(result, [(2, 3, 4, 5)])

    def test_nested_keys_and_list_paths_preserve_literal_slashes(self):
        data = {'/group': {'value/': 2}, 'items': [{'name/': 'first'}]}

        result = utils.parse_object(data)

        self.assertEqual(result, {'/group/value/': 2, 'items/0/name/': 'first'})

    def test_ordinary_paths_and_root_scalars(self):
        self.assertEqual(utils.parse_object({'group': {'value': 2}}), {'group/value': 2})
        self.assertEqual(utils.parse_object(2), {'': 2})
