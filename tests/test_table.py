#!/usr/bin/env python

import unittest2 as unittest

import journalism

class TestIntColumn(unittest.TestCase):
    def setUp(self):
        self.test_data = [1, 2, 4]
        self.column = journalism.IntColumn(self.test_data) 

    def test_validation(self):
        journalism.IntColumn(self.test_data, validate=True)

    def test_validation_fails(self):
        data = ['a', 2, 4]

        self.assertRaises(journalism.ColumnValidationError, journalism.IntColumn, [data], { 'validate': True })

    def test_sum(self):
        # TODO: override natural operator
        #self.assertEqual(sum(self.column), 7)
        
        self.assertEqual(self.column.sum(), 7)

class TestIntColumnWithNulls(unittest.TestCase):
    def setUp(self):
        self.test_data = [1, 2, None, 4, None]
        self.column = journalism.IntColumn(self.test_data)

    def test_sum(self):
        # TODO: override natural operator
        #self.assertEqual(sum(self.column), 7)
        
        self.assertEqual(self.column.sum(), 7)

    def test_mean(self):
        self.assertRaises(journalism.NullComputationError, self.column.mean)

    def test_median(self):
        self.assertRaises(journalism.NullComputationError, self.column.mean)
