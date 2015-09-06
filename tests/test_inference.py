#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate.column_types import *
from agate.inference import *

class TestTypeInference(unittest.TestCase):
    def setUp(self):
        pass

    def testTextType(self):
        rows = [
            ('a',),
            ('b',),
            ('',)
        ]

        inferred = infer_types(rows, ['one'])

        self.assertIsInstance(inferred[0][1], TextType)

    def testNumberType(self):
        rows = [
            ('1.7',),
            ('200000000',),
            ('',)
        ]

        inferred = infer_types(rows, ['one'])

        self.assertIsInstance(inferred[0][1], NumberType)

    def testBooleanType(self):
        rows = [
            ('True',),
            ('FALSE',),
            ('',)
        ]

        inferred = infer_types(rows, ['one'])

        self.assertIsInstance(inferred[0][1], BooleanType)

    def testDateTimeType(self):
        rows = [
            ('5/7/84 3:44:12',),
            ('2/28/1997 3:12 AM',),
            ('3/19/20',),
            ('',)
        ]

        inferred = infer_types(rows, ['one'])

        self.assertIsInstance(inferred[0][1], DateTimeType)

    def testTimeDeltaType(self):
        rows = [
            ('1:42',),
            ('1w 27h',),
            ('',)
        ]

        inferred = infer_types(rows, ['one'])

        self.assertIsInstance(inferred[0][1], TimeDeltaType)
