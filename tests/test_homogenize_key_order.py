from agate import Table
from agate.data_types import Text
from agate.testcase import AgateTestCase


class TestHomogenizeKeyOrder(AgateTestCase):
    def test_reversed_keys_keep_values_in_their_columns(self):
        table = Table([('old-a', 'old-b', 'old')], ['a', 'b', 'value'], [Text()] * 3)
        defaults = ['new']

        result = table.homogenize(['b', 'a'], [('new-b', 'new-a')], defaults)

        self.assertRows(result, [('old-a', 'old-b', 'old'), ('new-a', 'new-b', 'new')])
        self.assertEqual(defaults, ['new'])
        self.assertRows(table, [('old-a', 'old-b', 'old')])

    def test_nonadjacent_keys_with_default_nulls(self):
        table = Table([], ['first', 'a', 'middle', 'b', 'last'], [Text()] * 5)

        result = table.homogenize(['b', 'a'], [('new-b', 'new-a')])

        self.assertRows(result, [(None, 'new-a', None, 'new-b', None)])

    def test_callable_receives_values_in_key_order(self):
        table = Table([], ['a', 'b', 'value'], [Text()] * 3)
        received = []

        def default_row(values):
            received.append(values)
            return [values[1], values[0], 'new']

        result = table.homogenize(['b', 'a'], [('new-b', 'new-a')], default_row)

        self.assertEqual(received, [('new-b', 'new-a')])
        self.assertRows(result, [('new-a', 'new-b', 'new')])
