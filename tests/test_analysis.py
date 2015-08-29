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

    def stage_noop(self, data):
        pass

    def test_data_flow(self):
        analysis = Analysis(self.stage1, cache_dir=TEST_CACHE)
        analysis.then(self.stage2)

        data = {}

        analysis.run(data)

        self.assertEqual(data, {})
        self.assertEqual(self.data_before_stage1, {})
        self.assertEqual(self.data_after_stage1, { 'stage1': 5 })
        self.assertEqual(self.data_before_stage2, { 'stage1' : 5 })
        self.assertEqual(self.data_after_stage2, { 'stage1': 5, 'stage2': 25 })

    def test_caching(self):
        analysis = Analysis(self.stage1, cache_dir=TEST_CACHE)
        analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

    def test_descendent_fingerprint_deleted(self):
        analysis = Analysis(self.stage1, cache_dir=TEST_CACHE)
        stage2_analysis = analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        os.remove(stage2_analysis._cache_path())

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 2)

    def test_ancestor_fingerprint_deleted(self):
        analysis = Analysis(self.stage1, cache_dir=TEST_CACHE)
        analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        os.remove(analysis._cache_path())

        analysis.run()

        self.assertEqual(self.executed_stage1, 2)
        self.assertEqual(self.executed_stage2, 2)

    def test_cache_reused(self):
        analysis = Analysis(self.stage1, cache_dir=TEST_CACHE)
        analysis.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        analysis2 = Analysis(self.stage1, cache_dir=TEST_CACHE)
        analysis2.then(self.stage2)

        analysis2.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

    def test_ancestor_changed(self):
        analysis = Analysis(self.stage1, cache_dir=TEST_CACHE)
        noop = analysis.then(self.stage_noop)
        noop.then(self.stage2)

        analysis.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 1)

        analysis2 = Analysis(self.stage1, cache_dir=TEST_CACHE)
        analysis2.then(self.stage2)

        analysis2.run()

        self.assertEqual(self.executed_stage1, 1)
        self.assertEqual(self.executed_stage2, 2)
