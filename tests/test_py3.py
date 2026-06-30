import csv
import os
import platform
import sys
import unittest
from io import StringIO

from agate import csv_py3
from agate.exceptions import FieldSizeLimitError


class TestReader(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ['number', 'text', 'boolean', 'date', 'datetime', 'timedelta'],
            ['1', 'a', 'True', '2015-11-04', '2015-11-04T12:22:00', '0:04:15'],
            ['2', '👍', 'False', '2015-11-05', '2015-11-04T12:45:00', '0:06:18'],
            ['', 'b', '', '', '', '']
        ]

    def test_utf8(self):
        with open('examples/test.csv', encoding='utf-8') as f:
            rows = list(csv_py3.Reader(f))

        for a, b in zip(self.rows, rows):
            self.assertEqual(a, b)

    def test_reader_alias(self):
        with open('examples/test.csv', encoding='utf-8') as f:
            rows = list(csv_py3.reader(f))

        for a, b in zip(self.rows, rows):
            self.assertEqual(a, b)

    def test_properties(self):
        with open('examples/test.csv', encoding='utf-8') as f:
            reader = csv_py3.Reader(f)

            self.assertEqual(reader.dialect.delimiter, ',')
            self.assertEqual(reader.line_num, 0)

            next(reader)

            self.assertEqual(reader.line_num, 1)

    def test_line_numbers(self):
        with open('examples/test.csv', encoding='utf-8') as f:
            rows = list(csv_py3.Reader(f, line_numbers=True))

        sample_rows = [
            ['line_numbers', 'number', 'text', 'boolean', 'date', 'datetime', 'timedelta'],
            ['1', '1', 'a', 'True', '2015-11-04', '2015-11-04T12:22:00', '0:04:15'],
            ['2', '2', '👍', 'False', '2015-11-05', '2015-11-04T12:45:00', '0:06:18'],
            ['3', '', 'b', '', '', '', '']
        ]

        for a, b in zip(sample_rows, rows):
            self.assertEqual(a, b)


class TestFieldSizeLimit(unittest.TestCase):
    def setUp(self):
        self.lim = csv.field_size_limit()

        with open('.test.csv', 'w', encoding='utf-8') as f:
            f.write('a' * 10)

    def tearDown(self):
        # Resetting limit to avoid failure in other tests.
        csv.field_size_limit(self.lim)
        os.remove('.test.csv')

    def test_field_size_limit(self):
        # Testing field_size_limit for failure. Creating data using str * int.
        with open('.test.csv', encoding='utf-8') as f:
            c = csv_py3.Reader(f, field_size_limit=9)
            try:
                c.__next__()
            except FieldSizeLimitError:
                pass
            else:
                raise AssertionError('Expected FieldSizeLimitError')

        # Now testing higher field_size_limit.
        with open('.test.csv', encoding='utf-8') as f:
            c = csv_py3.Reader(f, field_size_limit=11)
            self.assertEqual(['a' * 10], c.__next__())


class TestWriter(unittest.TestCase):
    def test_utf8(self):
        output = StringIO()
        writer = csv_py3.Writer(output)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', 'ʤ'])

        written = StringIO(output.getvalue())

        reader = csv_py3.Reader(written)
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', 'ʤ'])

    def test_writer_alias(self):
        output = StringIO()
        writer = csv_py3.writer(output)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', 'ʤ'])

        written = StringIO(output.getvalue())

        reader = csv_py3.reader(written)
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', 'ʤ'])

    def test_line_numbers(self):
        output = StringIO()
        writer = csv_py3.Writer(output, line_numbers=True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', 'ʤ'])

        written = StringIO(output.getvalue())

        reader = csv_py3.Reader(written)
        self.assertEqual(next(reader), ['line_number', 'a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '1', '2', '3'])
        self.assertEqual(next(reader), ['2', '4', '5', 'ʤ'])

    def test_writerows(self):
        output = StringIO()
        writer = csv_py3.Writer(output)
        writer.writerows([
            ['a', 'b', 'c'],
            ['1', '2', '3'],
            ['4', '5', 'ʤ']
        ])

        written = StringIO(output.getvalue())

        reader = csv_py3.Reader(written)
        self.assertEqual(next(reader), ['a', 'b', 'c'])
        self.assertEqual(next(reader), ['1', '2', '3'])
        self.assertEqual(next(reader), ['4', '5', 'ʤ'])


class TestDictReader(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ['number', 'text', 'boolean', 'date', 'datetime', 'timedelta'],
            ['1', 'a', 'True', '2015-11-04', '2015-11-04T12:22:00', '0:04:15'],
            ['2', '👍', 'False', '2015-11-05', '2015-11-04T12:45:00', '0:06:18'],
            ['', 'b', '', '', '', '']
        ]

        self.f = open('examples/test.csv', encoding='utf-8')

    def tearDown(self):
        self.f.close()

    def test_reader(self):
        reader = csv_py3.DictReader(self.f)

        self.assertEqual(next(reader), dict(zip(self.rows[0], self.rows[1])))

    def test_reader_alias(self):
        reader = csv_py3.DictReader(self.f)

        self.assertEqual(next(reader), dict(zip(self.rows[0], self.rows[1])))


class TestDictWriter(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()

    def tearDown(self):
        self.output.close()

    def test_writer(self):
        writer = csv_py3.DictWriter(self.output, ['a', 'b', 'c'])
        writer.writeheader()
        writer.writerow({
            'a': '1',
            'b': '2',
            'c': '☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')

    def test_writer_alias(self):
        writer = csv_py3.DictWriter(self.output, ['a', 'b', 'c'])
        writer.writeheader()
        writer.writerow({
            'a': '1',
            'b': '2',
            'c': '☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\n1,2,☃\n')

    def test_line_numbers(self):
        writer = csv_py3.DictWriter(self.output, ['a', 'b', 'c'], line_numbers=True)
        writer.writeheader()
        writer.writerow({
            'a': '1',
            'b': '2',
            'c': '☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'line_number,a,b,c\n1,1,2,☃\n')

    def test_writerows(self):
        writer = csv_py3.DictWriter(self.output, ['a', 'b', 'c'], line_numbers=True)
        writer.writeheader()
        writer.writerows([{
            'a': '1',
            'b': '2',
            'c': '☃'
        }])

        result = self.output.getvalue()

        self.assertEqual(result, 'line_number,a,b,c\n1,1,2,☃\n')


class TestSniffer(unittest.TestCase):
    @unittest.skipIf(
        platform.system() == 'Darwin' and sys.version_info[:2] == (3, 10),
        reason='The (macos-latest, 3.10) job fails on GitHub Actions'
    )
    def test_sniffer(self):
        # The sniffed dialect is a dynamically-created class. Comparing its raw ``__dict__`` is
        # fragile: it carries version-specific dunders (e.g. ``__firstlineno__``,
        # ``__static_attributes__``), and the ``mappingproxy`` returned by ``__dict__`` does not
        # keep the class alive, so once it is garbage-collected the proxy reports an empty dict.
        # Instead, hold references to the dialects and compare their meaningful attributes.
        attributes = ('delimiter', 'doublequote', 'escapechar', 'lineterminator',
                      'quotechar', 'quoting', 'skipinitialspace')

        def dialect_attributes(dialect):
            return {attribute: getattr(dialect, attribute) for attribute in attributes}

        with open('examples/test.csv', encoding='utf-8') as f:
            contents = f.read()

        direct = dialect_attributes(csv.Sniffer().sniff(contents, csv_py3.POSSIBLE_DELIMITERS))
        actual = dialect_attributes(csv_py3.Sniffer().sniff(contents))
        expected = dialect_attributes(csv.Sniffer().sniff(contents))

        self.assertEqual(direct, expected, f'{direct!r} != {expected!r}')
        self.assertEqual(actual, expected, f'{actual!r} != {expected!r}')
