import unittest

from agate.mapped_sequence import MappedSequence


class TestMappedSequence(unittest.TestCase):
    def setUp(self):
        self.column_names = ('one', 'two', 'three')
        self.data = ('a', 'b', 'c')
        self.row = MappedSequence(self.data, self.column_names)

    def test_is_immutable(self):
        with self.assertRaises(TypeError):
            self.row[0] = 'foo'

        with self.assertRaises(TypeError):
            self.row['one'] = 100

    def test_stringify(self):
        self.assertEqual(str(self.row), "<agate.MappedSequence: ('a', 'b', 'c')>")

    def test_stringify_long(self):
        column_names = ('one', 'two', 'three', 'four', 'five', 'six')
        data = ('a', 'b', 'c', 'd', 'e', 'f')
        row = MappedSequence(data, column_names)

        self.assertEqual(str(row), "<agate.MappedSequence: ('a', 'b', 'c', 'd', 'e', ...)>")

    def test_length(self):
        self.assertEqual(len(self.row), 3)

    def test_eq(self):
        row2 = MappedSequence(self.data, self.column_names)

        self.assertTrue(self.row == ('a', 'b', 'c'))
        self.assertTrue(self.row == ['a', 'b', 'c'])
        self.assertTrue(self.row == row2)
        self.assertFalse(self.row == ('a', 'b', 'c', 'd'))
        self.assertFalse(self.row == 1)

    def test_ne(self):
        row2 = MappedSequence(self.data, self.column_names)

        self.assertFalse(self.row != ('a', 'b', 'c'))
        self.assertFalse(self.row != ['a', 'b', 'c'])
        self.assertFalse(self.row != row2)
        self.assertTrue(self.row != ('a', 'b', 'c', 'd'))
        self.assertTrue(self.row != 1)

    def test_contains(self):
        self.assertTrue('a' in self.row)
        self.assertFalse('d' in self.row)

    def test_set_item(self):
        with self.assertRaises(TypeError):
            self.row['one'] = 't'

        with self.assertRaises(TypeError):
            self.row['five'] = 'g'

    def test_get_item(self):
        self.assertEqual(self.row['one'], 'a')
        self.assertEqual(self.row['two'], 'b')
        self.assertEqual(self.row['three'], 'c')

    def test_get_by_key(self):
        self.assertEqual(self.row['one'], 'a')
        self.assertEqual(self.row[0], 'a')

    def test_get_by_slice(self):
        self.assertSequenceEqual(self.row[1:], ('b', 'c'))

    def test_get_invalid(self):
        with self.assertRaises(IndexError):
            self.row[3]

        with self.assertRaises(KeyError):
            self.row['foo']

    def test_keys(self):
        self.assertIs(self.row.keys(), self.column_names)

    def test_values(self):
        self.assertIs(self.row.values(), self.data)

    def test_items(self):
        self.assertSequenceEqual(self.row.items(), [
            ('one', 'a'),
            ('two', 'b'),
            ('three', 'c')
        ])

    def test_get(self):
        self.assertEqual(self.row.get('one'), 'a')

    def test_get_default(self):
        self.assertEqual(self.row.get('four'), None)
        self.assertEqual(self.row.get('four', 'foo'), 'foo')

    def test_dict(self):
        self.assertDictEqual(self.row.dict(), {
            'one': 'a',
            'two': 'b',
            'three': 'c'
        })

    def test_dict_no_keys(self):
        row = MappedSequence(self.data)

        with self.assertRaises(KeyError):
            row.dict()

    def test_iterate(self):
        it = iter(self.row)

        self.assertSequenceEqual(next(it), 'a')
        self.assertSequenceEqual(next(it), 'b')
        self.assertSequenceEqual(next(it), 'c')

        with self.assertRaises(StopIteration):
            next(it)
