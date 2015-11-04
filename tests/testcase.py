#!/usr/bin/env Python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class AgateTestCase(unittest.TestCase):
    def assertSequenceInstances(self, seq, type_seq):
        for s, t in zip(seq, type_seq):
            self.assertIsInstance(s, t)
