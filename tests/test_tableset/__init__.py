import json
import shutil
from collections import OrderedDict
from io import StringIO

from agate import Table, TableSet
from agate.computations import Formula
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestTableSet(AgateTestCase):
    def setUp(self):
        self.table1 = (
            ('a', 1),
            ('a', 3),
            ('b', 2)
        )

        self.table2 = (
            ('b', 0),
            ('a', 2),
            ('c', 5)
        )

        self.table3 = (
            ('a', 1),
            ('a', 2),
            ('c', 3)
        )

        self.text_type = Text()
        self.number_type = Number()

        self.column_names = ['letter', 'number']
        self.column_types = [self.text_type, self.number_type]

        self.tables = OrderedDict([
            ('table1', Table(self.table1, self.column_names, self.column_types)),
            ('table2', Table(self.table2, self.column_names, self.column_types)),
            ('table3', Table(self.table3, self.column_names, self.column_types))
        ])

    def test_create_tableset(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        self.assertEqual(len(tableset), 3)

    def test_create_tableset_mismatched_column_names(self):
        tables = OrderedDict([
            ('table1', Table(self.table1, self.column_names, self.column_types)),
            ('table2', Table(self.table2, self.column_names, self.column_types)),
            ('table3', Table(self.table3, ['foo', 'bar'], self.column_types))
        ])

        with self.assertRaises(ValueError):
            TableSet(tables.values(), tables.keys())

    def test_create_tableset_mismatched_column_types(self):
        tables = OrderedDict([
            ('table1', Table(self.table1, self.column_names, self.column_types)),
            ('table2', Table(self.table2, self.column_names, self.column_types)),
            ('table3', Table(self.table3, self.column_names, [self.text_type, self.text_type]))
        ])

        with self.assertRaises(ValueError):
            TableSet(tables.values(), tables.keys())

    def test_iter(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        for i, table in enumerate(tableset):
            self.assertEqual(table, list(self.tables.values())[i])

    def test_from_csv(self):
        tableset1 = TableSet(self.tables.values(), self.tables.keys())
        tableset2 = TableSet.from_csv('examples/tableset', self.column_names)

        self.assertSequenceEqual(tableset1.column_names, tableset2.column_names)
        self.assertSequenceEqual([type(t) for t in tableset1.column_types], [type(t) for t in tableset2.column_types])

        self.assertEqual(len(tableset1), len(tableset2))

        for name in ['table1', 'table2', 'table3']:
            self.assertEqual(len(tableset1[name].columns), len(tableset2[name].columns))
            self.assertEqual(len(tableset1[name].rows), len(tableset2[name].rows))

            self.assertSequenceEqual(tableset1[name].rows[0], tableset2[name].rows[0])
            self.assertSequenceEqual(tableset1[name].rows[1], tableset2[name].rows[1])
            self.assertSequenceEqual(tableset1[name].rows[2], tableset2[name].rows[2])

    def test_tableset_from_csv_invalid_dir(self):
        with self.assertRaises(IOError):
            TableSet.from_csv('quack')

    def test_from_csv_column_types_not_equal(self):
        with self.assertRaises(ValueError):
            TableSet.from_csv('examples/tableset/type_error')

    def test_to_csv(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        tableset.to_csv('.test-tableset')

        for name in ['table1', 'table2', 'table3']:
            with open('.test-tableset/%s.csv' % name) as f:
                contents1 = f.read()

            with open('examples/tableset/%s.csv' % name) as f:
                contents2 = f.read()

            self.assertEqual(contents1, contents2)

        shutil.rmtree('.test-tableset')

    def test_from_json_dir(self):
        tableset1 = TableSet(self.tables.values(), self.tables.keys())
        tableset2 = TableSet.from_json('examples/tableset')

        self.assertSequenceEqual(tableset1.column_names, tableset2.column_names)
        self.assertSequenceEqual([type(t) for t in tableset1.column_types], [type(t) for t in tableset2.column_types])

        self.assertEqual(len(tableset1), len(tableset2))

        for name in ['table1', 'table2', 'table3']:
            self.assertEqual(len(tableset1[name].columns), len(tableset2[name].columns))
            self.assertEqual(len(tableset1[name].rows), len(tableset2[name].rows))

            self.assertSequenceEqual(tableset1[name].rows[0], tableset2[name].rows[0])
            self.assertSequenceEqual(tableset1[name].rows[1], tableset2[name].rows[1])
            self.assertSequenceEqual(tableset1[name].rows[2], tableset2[name].rows[2])

    def test_from_json_file(self):
        tableset1 = TableSet(self.tables.values(), self.tables.keys())
        tableset2 = TableSet.from_json('examples/test_tableset.json')

        with open('examples/test_tableset.json') as f:
            filelike = StringIO(f.read())

        tableset3 = TableSet.from_json(filelike)

        self.assertSequenceEqual(tableset1.column_names, tableset2.column_names, tableset3.column_names)
        self.assertSequenceEqual(
            [type(t) for t in tableset1.column_types],
            [type(t) for t in tableset2.column_types],
            [type(t) for t in tableset3.column_types]
        )

        self.assertEqual(len(tableset1), len(tableset2), len(tableset3))

        for name in ['table1', 'table2', 'table3']:
            self.assertEqual(len(tableset1[name].columns), len(tableset2[name].columns), len(tableset3[name].columns))
            self.assertEqual(len(tableset1[name].rows), len(tableset2[name].rows), len(tableset3[name].rows))

            self.assertSequenceEqual(tableset1[name].rows[0], tableset2[name].rows[0], tableset3[name].rows[0])
            self.assertSequenceEqual(tableset1[name].rows[1], tableset2[name].rows[1], tableset3[name].rows[1])
            self.assertSequenceEqual(tableset1[name].rows[2], tableset2[name].rows[2], tableset3[name].rows[2])

    def test_from_json_false_path(self):
        with self.assertRaises(IOError):
            TableSet.from_json('notapath')

    def test_to_json(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        tableset.to_json('.test-tableset')

        for name in ['table1', 'table2', 'table3']:
            with open('.test-tableset/%s.json' % name) as f:
                contents1 = json.load(f)

            with open('examples/tableset/%s.json' % name) as f:
                contents2 = json.load(f)

            self.assertEqual(contents1, contents2)

        shutil.rmtree('.test-tableset')

    def test_to_nested_json(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        output = StringIO()
        tableset.to_json(output, nested=True)
        tableset.to_json('.test-tableset/tableset.json', nested=True)

        contents1 = json.loads(output.getvalue())

        with open('.test-tableset/tableset.json') as f:
            contents2 = json.load(f)

        with open('examples/test_tableset.json') as f:
            contents3 = json.load(f)

        self.assertEqual(contents1, contents3)
        self.assertEqual(contents2, contents3)

        shutil.rmtree('.test-tableset')

    def test_get_column_types(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        self.assertSequenceEqual(tableset.column_types, self.column_types)

    def test_get_column_names(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        self.assertSequenceEqual(tableset.column_names, self.column_names)

    def test_compute(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_tableset = tableset.compute([
            ('new_column', Formula(self.text_type, lambda r: '%(letter)s-%(number)i' % r))
        ])

        new_table = new_tableset['table1']

        self.assertColumnNames(new_table, ('letter', 'number', 'new_column',))
        self.assertColumnTypes(new_table, (Text, Number, Text))
        self.assertRows(new_table, [
            ('a', 1, 'a-1'),
            ('a', 3, 'a-3'),
            ('b', 2, 'b-2')
        ])

        new_table = new_tableset['table2']

        self.assertRows(new_table, [
            ('b', 0, 'b-0'),
            ('a', 2, 'a-2'),
            ('c', 5, 'c-5')
        ])

        new_table = new_tableset['table3']

        self.assertSequenceEqual(new_table.rows[0], ('a', 1, 'a-1'))
        self.assertSequenceEqual(new_table.rows[1], ('a', 2, 'a-2'))
        self.assertSequenceEqual(new_table.rows[2], ('c', 3, 'c-3'))

    def test_select(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        new_tableset = tableset.select(['number'])

        for name, new_table in new_tableset.items():
            self.assertColumnNames(new_table, ('number',))
            self.assertColumnTypes(new_table, (Number,))

    def test_print_structure(self):
        tableset = TableSet(self.tables.values(), self.tables.keys())

        output = StringIO()
        tableset.print_structure(output=output)
        lines = output.getvalue().strip().split('\n')

        self.assertEqual(len(lines), 5)

    def test_print_structure_row_limit(self):
        tables = self.tables
        for i in range(25):
            tables[str(i)] = self.tables['table1']

        tableset = TableSet(tables.values(), tables.keys())
        output = StringIO()
        tableset.print_structure(output=output)
        lines = output.getvalue().strip().split('\n')

        self.assertEqual(len(lines), 22)

    def test_nested(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='test')

        nested = tableset.group_by('letter')

        self.assertIsInstance(nested, TableSet)
        self.assertEqual(len(nested), 3)
        self.assertSequenceEqual(nested._column_names, ('letter', 'number'))
        self.assertSequenceEqual(nested._column_types, (self.text_type, self.number_type))

        self.assertIsInstance(nested['table1'], TableSet)
        self.assertEqual(len(nested['table1']), 2)
        self.assertSequenceEqual(nested['table1']._column_names, ('letter', 'number'))
        self.assertSequenceEqual(nested['table1']._column_types, (self.text_type, self.number_type))

        self.assertIsInstance(nested['table1']['a'], Table)
        self.assertEqual(len(nested['table1']['a'].columns), 2)
        self.assertEqual(len(nested['table1']['a'].rows), 2)

    def test_proxy_local(self):
        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='foo')

        self.assertEqual(tableset._key_name, 'foo')

    def test_proxy_maintains_key(self):
        number_type = Number()

        tableset = TableSet(self.tables.values(), self.tables.keys(), key_name='foo', key_type=number_type)

        self.assertEqual(tableset.key_name, 'foo')
        self.assertEqual(tableset.key_type, number_type)

        new_tableset = tableset.select(['number'])

        self.assertEqual(new_tableset.key_name, 'foo')
        self.assertEqual(new_tableset.key_type, number_type)
