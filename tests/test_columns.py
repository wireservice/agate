#!/usr/bin/env python

import mock
import unittest2 as unittest

import journalism

class TestIntColumn(unittest.TestCase):
    def setUp(self):
        self.test_data = [1, 2, 4, 2]

        self.mock_table = mock.Mock()
        self.mock_table._get_column_data.return_value = self.test_data

        self.column = journalism.IntColumn(self.mock_table, 'test') 

    def test_validation(self):
        journalism.IntColumn(self.mock_table, 'test', validate=True)

    def test_validation_fails(self):
        self.mock_table._get_column_data.return_value = ['a', 2, 4]

        with self.assertRaises(journalism.ColumnValidationError):
            journalism.IntColumn(self.mock_table, 'test', validate=True)

    def test_unique(self):
        self.assertEqual(self.column.unique(), set([1, 2, 4]))

    def test_sum(self):
        # TODO: override natural operator
        #self.assertEqual(sum(self.column), 9)
        
        self.assertEqual(self.column.sum(), 9)

class TestIntColumnWithNulls(unittest.TestCase):
    def setUp(self):
        self.test_data = [1, 2, None, 4, None]

        self.mock_table = mock.Mock()
        self.mock_table._get_column_data.return_value = self.test_data
 
        self.column = journalism.IntColumn(self.mock_table, 'test')

    def test_sum(self):
        # TODO: override natural operator
        #self.assertEqual(sum(self.column), 7)
        
        self.assertEqual(self.column.sum(), 7)

    def test_mean(self):
        self.assertRaises(journalism.NullComputationError, self.column.mean)

    def test_median(self):
        self.assertRaises(journalism.NullComputationError, self.column.mean)
