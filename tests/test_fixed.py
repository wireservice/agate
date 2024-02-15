import unittest

from agate import csv, fixed


class TestFixed(unittest.TestCase):
    def test_reader(self):
        with open('examples/testfixed_converted.csv') as f:
            csv_reader = csv.Reader(f)
            csv_header = next(csv_reader)
            csv_data = list(csv_reader)

        with open('examples/testfixed') as f:
            with open('examples/testfixed_schema.csv') as schema_f:
                fixed_reader = fixed.Reader(f, schema_f)
                fixed_data = list(fixed_reader)

        self.assertEqual(csv_header, fixed_reader.fieldnames)
        self.assertEqual(csv_data, fixed_data)

    def test_reader_func(self):
        with open('examples/testfixed_converted.csv') as f:
            csv_reader = csv.reader(f)
            csv_header = next(csv_reader)
            csv_data = list(csv_reader)

        with open('examples/testfixed') as f:
            with open('examples/testfixed_schema.csv') as schema_f:
                fixed_reader = fixed.reader(f, schema_f)
                fixed_data = list(fixed_reader)

        self.assertEqual(csv_header, fixed_reader.fieldnames)
        self.assertEqual(csv_data, fixed_data)

    def test_dict_reader(self):
        with open('examples/testfixed_converted.csv') as f:
            csv_reader = csv.DictReader(f)
            csv_data = list(csv_reader)

        with open('examples/testfixed') as f:
            with open('examples/testfixed_schema.csv') as schema_f:
                fixed_reader = fixed.DictReader(f, schema_f)
                fixed_data = list(fixed_reader)

        self.assertEqual(csv_reader.fieldnames, fixed_reader.fieldnames)
        self.assertEqual(csv_data, fixed_data)
