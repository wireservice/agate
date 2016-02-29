#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six

import agate


class TestCSV(unittest.TestCase):
    def test_agate(self):
        if six.PY2:
            self.assertIs(agate.csv.reader, agate.csv_py2.reader)
            self.assertIs(agate.csv.writer, agate.csv_py2.writer)
            self.assertIs(agate.csv.DictReader, agate.csv_py2.DictReader)
            self.assertIs(agate.csv.DictWriter, agate.csv_py2.DictWriter)
        else:
            self.assertIs(agate.csv.reader, agate.csv_py3.reader)
            self.assertIs(agate.csv.writer, agate.csv_py3.writer)
            self.assertIs(agate.csv.DictReader, agate.csv_py3.DictReader)
            self.assertIs(agate.csv.DictWriter, agate.csv_py3.DictWriter)
