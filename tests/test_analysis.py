#!/usr/bin/env Python

from copy import deepcopy
import os
import shutil
from time import sleep

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate.analysis import Analysis
from agate.column_types import NumberType, TextType
from agate.table import Table

TEST_CACHE = '.agate-test'

def wait_for_create(path):
    while not os.path.exists(path):
        sleep(1)

def wait_for_delete(path):
    while os.path.exists(path):
        sleep(1)

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.executed_stage1 = 0
        self.data_before_stage1 = None
        self.data_after_stage1 = None

        self.executed_stage2 = 0
        self.data_before_stage2 = None
        self.data_after_stage2 = None

    def tearDown(self):
        shutil.rmtree(TEST_CACHE)

    def stage1(self, data):
        self.executed_stage1 += 1
        self.data_before_stage1 = deepcopy(data)

        data['stage1'] = 5

        self.data_after_stage1 = deepcopy(data)

    def stage2(self, data):
        self.executed_stage2 += 1
        self.data_before_stage2 = deepcopy(data)

        data['stage2'] = data['stage1'] * 5

        self.data_after_stage2 = deepcopy(data)

    def test_data_flow(self):
        analysis = Analysis(self.stage1, cache_path=TEST_CACHE)
        analysis.then(self.stage2)

        data = {}

        analysis.run(data)

        self.assertEqual(data, {})
        self.assertEqual(self.data_before_stage1, {})
        self.assertEqual(self.data_after_stage1, { 'stage1': 5 })
        self.assertEqual(self.data_before_stage2, { 'stage1' : 5 })
        self.assertEqual(self.data_after_stage2, { 'stage1': 5, 'stage2': 25 })

    def test_caching(self):
        analysis = Analysis(self.stage1, cache_path=TEST_CACHE)
        analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

    def test_descendent_fingerprint_deleted(self):
        analysis = Analysis(self.stage1, cache_path=TEST_CACHE)
        analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        path = os.path.join(TEST_CACHE, 'stage2.fingerprint')
        os.remove(path)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 2)

    def test_ancestor_fingerprint_deleted(self):
        analysis = Analysis(self.stage1, cache_path=TEST_CACHE)
        analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        path = os.path.join(TEST_CACHE, 'stage1.fingerprint')
        os.remove(path)

        analysis.run()

        self.assertEqual(self.executed_stage1, 2)
        self.assertEqual(self.executed_stage2, 2)

    def test_descendent_fingerprint_mismatch(self):
        analysis = Analysis(self.stage1, cache_path=TEST_CACHE)
        analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        path = os.path.join(TEST_CACHE, 'stage2.fingerprint')

        with open(path, 'w') as f:
            f.write('foo')

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 2)

    def test_ancestor_fingerprint_mismatch(self):
        analysis = Analysis(self.stage1, cache_path=TEST_CACHE)
        analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        path = os.path.join(TEST_CACHE, 'stage1.fingerprint')

        with open(path, 'w') as f:
            f.write('foo')

        analysis.run()

        self.assertEqual(self.executed_stage1, 2)
        self.assertEqual(self.executed_stage2, 2)
