#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import journalism

class TestTable(unittest.TestCase):
    def test_journalism(self):
        with self.assertRaises(NotImplementedError):
            journalism.save()
