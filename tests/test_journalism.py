#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import agate

class TestTable(unittest.TestCase):
    def test_agate(self):
        with self.assertRaises(NotImplementedError):
            agate.save()
