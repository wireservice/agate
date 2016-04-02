#!/usr/bin/env python
# -*- coding: utf8 -*-

from random import shuffle
from timeit import Timer

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six
from six.moves import range

import agate


class TestTableCompute(unittest.TestCase):
    def test_compute(self):
        rows = [(six.text_type(i), i) for i in range(100000)]

        shuffle(rows)

        column_names = ['text', 'number']
        column_types = [agate.Text(), agate.Number()]

        table = agate.Table(rows, column_names, column_types)

        def test():
            table.compute([
                ('test', agate.Formula(agate.Text(), lambda row: '%(text)s-%(number)s' % row)),
            ])

        results = Timer(test).repeat(10, 1)

        min_time = min(results)

        self.assertLess(min_time, 0)
