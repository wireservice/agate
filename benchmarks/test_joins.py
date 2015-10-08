#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

from random import shuffle
from timeit import Timer

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six
from six.moves import range

import agate

class TestTableJoin(unittest.TestCase):
    def test_join(self):
        left_rows = [(six.text_type(i), i) for i in range(100000)]
        right_rows = [(six.text_type(i), i) for i in range(100000)]

        shuffle(left_rows)
        shuffle(right_rows)

        number_type = agate.Number()
        text_type = agate.Text()

        columns = (
            ('text', text_type),
            ('number', number_type)
        )

        left = agate.Table(left_rows, columns)
        right = agate.Table(right_rows, columns)

        def test():
            left.join(right, 'text')

        results = Timer(test).repeat(10, 1)

        min_time = min(results)

        self.assertLess(min_time, 0)
