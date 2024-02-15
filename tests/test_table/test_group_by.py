from decimal import Decimal

from agate import Table, TableSet
from agate.data_types import Boolean, Number, Text
from agate.testcase import AgateTestCase


class TestGroupBy(AgateTestCase):
    def setUp(self):
        self.rows = (
            ('a', 2, 3, 4),
            (None, 3, 5, None),
            ('a', 2, 4, None),
            ('b', 3, 4, None)
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = [
            'one', 'two', 'three', 'four'
        ]
        self.column_types = [
            self.text_type, self.number_type, self.number_type, self.number_type
        ]

    def test_group_by(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by('one')

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(len(tableset), 3)
        self.assertEqual(tableset.key_name, 'one')
        self.assertIsInstance(tableset.key_type, Text)

        self.assertIn('a', tableset.keys())
        self.assertIn('b', tableset.keys())
        self.assertIn(None, tableset.keys())

        self.assertSequenceEqual(tableset['a'].columns['one'], ('a', 'a'))
        self.assertSequenceEqual(tableset['b'].columns['one'], ('b',))

    def test_group_by_number(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by('two')

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(len(tableset), 2)
        self.assertEqual(tableset.key_name, 'two')
        self.assertIsInstance(tableset.key_type, Number)

        self.assertIn(Decimal('2'), tableset.keys())
        self.assertIn(Decimal('3'), tableset.keys())

        self.assertSequenceEqual(tableset[Decimal('2')].columns['one'], ('a', 'a'))
        self.assertSequenceEqual(tableset[Decimal('3')].columns['one'], (None, 'b'))

    def test_group_by_key_name(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by('one', key_name='test')

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(tableset.key_name, 'test')
        self.assertIsInstance(tableset.key_type, Text)

        self.assertIn('a', tableset.keys())
        self.assertIn('b', tableset.keys())
        self.assertIn(None, tableset.keys())

        self.assertSequenceEqual(tableset['a'].columns['one'], ('a', 'a'))
        self.assertSequenceEqual(tableset['b'].columns['one'], ('b',))

    def test_group_by_key_type(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by('two', key_type=Text())

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(tableset.key_name, 'two')
        self.assertIsInstance(tableset.key_type, Text)

        self.assertIn('2', tableset.keys())
        self.assertIn('3', tableset.keys())

        self.assertSequenceEqual(tableset['2'].columns['one'], ('a', 'a'))
        self.assertSequenceEqual(tableset['3'].columns['one'], (None, 'b'))

    def test_group_by_function(self):
        table = Table(self.rows, self.column_names, self.column_types)

        tableset = table.group_by(lambda r: r['three'] < 5, key_type=Boolean())

        self.assertIsInstance(tableset, TableSet)
        self.assertEqual(len(tableset), 2)
        self.assertEqual(tableset.key_name, 'group')

        self.assertIn(True, tableset.keys())
        self.assertIn(False, tableset.keys())

        self.assertSequenceEqual(tableset[True].columns['one'], ('a', 'a', 'b'))
        self.assertSequenceEqual(tableset[False].columns['one'], (None,))

    def test_group_by_bad_column(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with self.assertRaises(KeyError):
            table.group_by('bad')
