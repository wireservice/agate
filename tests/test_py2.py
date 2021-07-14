#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six

from agate import csv_py2
from agate.exceptions import FieldSizeLimitError


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestUnicodeReader(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ['number', 'text', 'boolean', 'date', 'datetime', 'timedelta'],
            ['1', 'a', 'True', '2015-11-04', '2015-11-04T12:22:00', '0:04:15'],
            ['2', u'👍', 'False', '2015-11-05', '2015-11-04T12:45:00', '0:06:18'],
            ['', 'b', '', '', '', '']
        ]

    def test_utf8(self):
        with open('examples/test.csv') as f:
            rows = list(csv_py2.UnicodeReader(f, encoding='utf-8'))

        for a, b in zip(self.rows, rows):
            self.assertEqual(a, b)

    def test_latin1(self):
        with open('examples/test_latin1.csv') as f:
            reader = csv_py2.UnicodeReader(f, encoding='latin1')
            self.assertEqual(next(reader), ['a', 'b', 'c'])
            self.assertEqual(next(reader), ['1', '2', '3'])
            self.assertEqual(next(reader), ['4', '5', u'©'])

    def test_utf16_big(self):
        with open('examples/test_utf16_big.csv') as f:
            reader = csv_py2.UnicodeReader(f, encoding='utf-16')
            self.assertEqual(next(reader), ['a', 'b', 'c'])
            self.assertEqual(next(reader), ['1', '2', '3'])
            self.assertEqual(next(reader), ['4', '5', u'ʤ'])

    def test_utf16_little(self):
        with open('examples/test_utf16_little.csv') as f:
            reader = csv_py2.UnicodeReader(f, encoding='utf-16')
            self.assertEqual(next(reader), ['a', 'b', 'c'])
            self.assertEqual(next(reader), ['1', '2', '3'])
            self.assertEqual(next(reader), ['4', '5', u'ʤ'])


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestUnicodeWriter(unittest.TestCase):
    def test_utf8(self):
        output = six.StringIO()
        writer = csv_py2.UnicodeWriter(output, encoding='utf-8')
        self.assertEqual(writer._eight_bit, True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csv_py2.UnicodeReader(written, encoding='utf-8')
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'ʤ'])

    def test_latin1(self):
        output = six.StringIO()
        writer = csv_py2.UnicodeWriter(output, encoding='latin1')
        self.assertEqual(writer._eight_bit, True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'©'])

        written = six.StringIO(output.getvalue())

        reader = csv_py2.UnicodeReader(written, encoding='latin1')
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'©'])

    def test_utf16_big(self):
        output = six.StringIO()
        writer = csv_py2.UnicodeWriter(output, encoding='utf-16-be')
        self.assertEqual(writer._eight_bit, False)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csv_py2.UnicodeReader(written, encoding='utf-16-be')
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'\u02A4'])

    def test_utf16_little(self):
        output = six.StringIO()
        writer = csv_py2.UnicodeWriter(output, encoding='utf-16-le')
        self.assertEqual(writer._eight_bit, False)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csv_py2.UnicodeReader(written, encoding='utf-16-le')
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'\u02A4'])


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestUnicodeDictReader(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ['number', 'text', 'boolean', 'date', 'datetime', 'timedelta'],
            ['1', 'a', 'True', '2015-11-04', '2015-11-04T12:22:00', '0:04:15'],
            ['2', u'👍', 'False', '2015-11-05', '2015-11-04T12:45:00', '0:06:18'],
            ['', 'b', '', '', '', '']
        ]

        self.f = open('examples/test.csv')

    def tearDown(self):
        self.f.close()

    def test_reader(self):
        reader = csv_py2.UnicodeDictReader(self.f, encoding='utf-8')

        self.assertEqual(next(reader), dict(zip(self.rows[0], self.rows[1])))

    def test_latin1(self):
        with open('examples/test_latin1.csv') as f:
            reader = csv_py2.UnicodeDictReader(f, encoding='latin1')
            self.assertEqual(next(reader), {
                u'a': u'1',
                u'b': u'2',
                u'c': u'3'
            })
            self.assertEqual(next(reader), {
                u'a': u'4',
                u'b': u'5',
                u'c': u'©'
            })


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestUnicodeDictWriter(unittest.TestCase):
    def setUp(self):
        self.output = six.StringIO()

    def tearDown(self):
        self.output.close()

    def test_writer(self):
        writer = csv_py2.UnicodeDictWriter(self.output, ['a', 'b', 'c'], lineterminator='\n')
        writer.writeheader()
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestFieldSizeLimit(unittest.TestCase):
    def setUp(self):
        self.lim = csv.field_size_limit()

        with open('.test.csv', 'w') as f:
            f.write('a' * 10)

    def tearDown(self):
        # Resetting limit to avoid failure in other tests.
        csv.field_size_limit(self.lim)
        os.remove('.test.csv')

    def test_field_size_limit(self):
        # Testing field_size_limit for failure. Creating data using str * int.
        with open('.test.csv', 'r') as f:
            c = csv_py2.UnicodeReader(f, field_size_limit=9)
            try:
                c.next()
            except FieldSizeLimitError:
                pass
            else:
                raise AssertionError('Expected FieldSizeLimitError')

        # Now testing higher field_size_limit.
        with open('.test.csv', 'r') as f:
            c = csv_py2.UnicodeReader(f, field_size_limit=11)
            self.assertEqual(['a' * 10], c.next())


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestReader(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ['number', 'text', 'boolean', 'date', 'datetime', 'timedelta'],
            ['1', 'a', 'True', '2015-11-04', '2015-11-04T12:22:00', '0:04:15'],
            ['2', u'👍', 'False', '2015-11-05', '2015-11-04T12:45:00', '0:06:18'],
            ['', 'b', '', '', '', '']
        ]

    def test_utf8(self):
        with open('examples/test.csv') as f:
            rows = list(csv_py2.Reader(f, encoding='utf-8'))

        for a, b in zip(self.rows, rows):
            self.assertEqual(a, b)

    def test_reader_alias(self):
        with open('examples/test.csv') as f:
            rows = list(csv_py2.Reader(f, encoding='utf-8'))

        for a, b in zip(self.rows, rows):
            self.assertEqual(a, b)

    def test_line_numbers(self):
        with open('examples/test.csv') as f:
            rows = list(csv_py2.Reader(f, encoding='utf-8', line_numbers=True))

        sample_rows = [
            ['line_numbers', 'number', 'text', 'boolean', 'date', 'datetime', 'timedelta'],
            ['1', '1', 'a', 'True', '2015-11-04', '2015-11-04T12:22:00', '0:04:15'],
            ['2', '2', u'👍', 'False', '2015-11-05', '2015-11-04T12:45:00', '0:06:18'],
            ['3', '', 'b', '', '', '', '']
        ]

        for a, b in zip(sample_rows, rows):
            self.assertEqual(a, b)

    def test_properties(self):
        with open('examples/test.csv') as f:
            reader = csv_py2.Reader(f, encoding='utf-8')

            self.assertEqual(reader.dialect.delimiter, ',')
            self.assertEqual(reader.line_num, 0)

            next(reader)

            self.assertEqual(reader.line_num, 1)


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestWriter(unittest.TestCase):
    def test_utf8(self):
        output = six.StringIO()
        writer = csv_py2.Writer(output, encoding='utf-8')
        self.assertEqual(writer._eight_bit, True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csv_py2.Reader(written, encoding='utf-8')
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'ʤ'])

    def test_writer_alias(self):
        output = six.StringIO()
        writer = csv_py2.writer(output, encoding='utf-8')
        self.assertEqual(writer._eight_bit, True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = six.StringIO(output.getvalue())

        reader = csv_py2.reader(written, encoding='utf-8')
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', u'ʤ'])


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestDictReader(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ['number', 'text', 'boolean', 'date', 'datetime', 'timedelta'],
            ['1', 'a', 'True', '2015-11-04', '2015-11-04T12:22:00', '0:04:15'],
            ['2', u'👍', 'False', '2015-11-05', '2015-11-04T12:45:00', '0:06:18'],
            ['', 'b', '', '', '', '']
        ]

        self.f = open('examples/test.csv')

    def tearDown(self):
        self.f.close()

    def test_reader(self):
        reader = csv_py2.DictReader(self.f, encoding='utf-8')

        self.assertEqual(next(reader), dict(zip(self.rows[0], self.rows[1])))

    def test_reader_alias(self):
        reader = csv_py2.DictReader(self.f, encoding='utf-8')

        self.assertEqual(next(reader), dict(zip(self.rows[0], self.rows[1])))


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestDictWriter(unittest.TestCase):
    def setUp(self):
        self.output = six.StringIO()

    def tearDown(self):
        self.output.close()

    def test_writer(self):
        writer = csv_py2.DictWriter(self.output, ['a', 'b', 'c'])
        writer.writeheader()
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')

    def test_writer_alias(self):
        writer = csv_py2.DictWriter(self.output, ['a', 'b', 'c'])
        writer.writeheader()
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')


@unittest.skipIf(six.PY3, "Not supported in Python 3.")
class TestSniffer(unittest.TestCase):
    def test_sniffer(self):
        with open('examples/test.csv') as f:
            contents = f.read()
            self.assertEqual(csv_py2.Sniffer().sniff(contents).__dict__, csv.Sniffer().sniff(contents).__dict__)
