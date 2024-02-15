import unittest
from random import shuffle
from timeit import Timer

import agate


class TestTableJoin(unittest.TestCase):
    def test_join(self):
        left_rows = [(str(i), i) for i in range(100000)]
        right_rows = [(str(i), i) for i in range(100000)]

        shuffle(left_rows)
        shuffle(right_rows)

        column_names = ['text', 'number']
        column_types = [agate.Text(), agate.Number()]

        left = agate.Table(left_rows, column_names, column_types)
        right = agate.Table(right_rows, column_names, column_types)

        def test():
            left.join(right, 'text')

        results = Timer(test).repeat(10, 1)

        min_time = min(results)

        self.assertLess(min_time, 20)  # CI unreliable, 15s witnessed on PyPy
