import unittest

import agate


class TestCSV(unittest.TestCase):
    def test_agate(self):
        self.assertIs(agate.csv.reader, agate.csv_py3.reader)
        self.assertIs(agate.csv.writer, agate.csv_py3.writer)
        self.assertIs(agate.csv.DictReader, agate.csv_py3.DictReader)
        self.assertIs(agate.csv.DictWriter, agate.csv_py3.DictWriter)
