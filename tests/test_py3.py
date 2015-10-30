#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate import csv_py3

@unittest.skipIf(six.PY2, "Not supported in Python 2.")
class TestReader(unittest.TestCase):
    def test_utf8(self):
        with open('examples/test.csv', encoding='utf-8') as f:
            reader = csv_py3.Reader(f)
            self.assertEqual(next(reader), ['one', 'two', 'three'])
            self.assertEqual(next(reader), ['1', '4', 'a'])
            self.assertEqual(next(reader), ['2', '3', 'b'])
            self.assertEqual(next(reader), ['', '2', u'👍'])

    def test_reader_alias(self):
        with open('examples/test.csv', encoding='utf-8') as f:
            reader = csv_py3.reader(f)
            self.assertEqual(next(reader), ['one', 'two', 'three'])
            self.assertEqual(next(reader), ['1', '4', 'a'])
            self.assertEqual(next(reader), ['2', '3', 'b'])
            self.assertEqual(next(reader), ['', '2', u'👍'])


@unittest.skipIf(six.PY2, "Not supported in Python 2.")
class TestWriter(unittest.TestCase):
    def test_utf8(self):
        output = six.StringIO()
        writer = csv_py3.Writer(output)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csv_py3.Reader(written)
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'ʤ'])

    def test_writer_alias(self):
        output = six.StringIO()
        writer = csv_py3.writer(output)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csv_py3.reader(written)
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'ʤ'])


@unittest.skipIf(six.PY2, "Not supported in Python 2.")
class TestDictReader(unittest.TestCase):
    def setUp(self):
        self.f = open('examples/test.csv')

    def tearDown(self):
        self.f.close()

    def test_reader(self):
        reader = csv_py3.DictReader(self.f)

        self.assertEqual(next(reader), {
            u'one': u'1',
            u'two': u'4',
            u'three': u'a'
        })

    def test_reader_alias(self):
        reader = csv_py3.DictReader(self.f)

        self.assertEqual(next(reader), {
            u'one': u'1',
            u'two': u'4',
            u'three': u'a'
        })

@unittest.skipIf(six.PY2, "Not supported in Python 2.")
class TestDictWriter(unittest.TestCase):
    def setUp(self):
        self.output = six.StringIO()

    def tearDown(self):
        self.output.close()

    def test_writer(self):
        writer = csv_py3.DictWriter(self.output, ['a', 'b', 'c'])
        writer.writeheader()
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')

    def test_writer_alias(self):
        writer = csv_py3.DictWriter(self.output, ['a', 'b', 'c'])
        writer.writeheader()
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')
