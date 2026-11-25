import json
import os
import tempfile

from agate import TableSet
from agate.data_types import Number
from agate.testcase import AgateTestCase


class TestTableSetFilenameStems(AgateTestCase):
    def test_csv_stems_do_not_collide(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, value in [('sales', 2), ('sale', 3)]:
                with open(os.path.join(directory, name + '.csv'), 'w') as output:
                    output.write('value\n%s\n' % value)

            result = TableSet.from_csv(directory, column_types=[Number()])

        self.assertEqual(sorted(result.keys()), ['sale', 'sales'])
        self.assertRows(result['sales'], [(2,)])
        self.assertRows(result['sale'], [(3,)])

    def test_json_stems_do_not_collide(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, value in [('john', 2), ('johns', 3)]:
                with open(os.path.join(directory, name + '.json'), 'w') as output:
                    json.dump([{'value': value}], output)

            result = TableSet.from_json(directory, column_types=[Number()])

        self.assertEqual(sorted(result.keys()), ['john', 'johns'])
        self.assertRows(result['john'], [(2,)])
        self.assertRows(result['johns'], [(3,)])
