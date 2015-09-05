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

        inferred = infer_types(rows)

        self.assertIsInstance(inferred[0], TextType)

    def testNumberType(self):
        rows = [
            ('1.7',),
            ('200000000',),
            ('',)
        ]

        inferred = infer_types(rows)

        self.assertIsInstance(inferred[0], NumberType)

    def testBooleanType(self):
        rows = [
            ('True',),
            ('FALSE',),
            ('',)
        ]

        inferred = infer_types(rows)

        self.assertIsInstance(inferred[0], BooleanType)

    def testDateType(self):
        rows = [
            ('5/7/84',),
            ('2/28/1997',),
            ('',)
        ]

        inferred = infer_types(rows)

        self.assertIsInstance(inferred[0], DateType)

    def testDateTimeType(self):
        rows = [
            ('5/7/84 3:44:12',),
            ('2/28/1997 3:12 AM',),
            ('',)
        ]

        inferred = infer_types(rows)

        self.assertIsInstance(inferred[0], DateTimeType)

    def testTimeDeltaType(self):
        rows = [
            ('1:42',),
            ('1w 27h',),
            ('',)
        ]

        inferred = infer_types(rows)

        self.assertIsInstance(inferred[0], TimeDeltaType)
