#!/usr/bin/env python
# -*- coding: utf8 -*-

import json

from collections import OrderedDict

from agate import Table
from agate.testcase import AgateTestCase
from agate.data_types import *


class TestDict(AgateTestCase):
    def setUp(self):
        self.rows = (
            (1, 'a', True, '11/4/2015', '11/4/2015 12:22 PM', '4:15'),
            (2, u'👍', False, '11/5/2015', '11/4/2015 12:45 PM', '6:18'),
            (None, 'b', None, None, None, None)
        )

        self.column_names = [
            'number', 'text', 'boolean', 'date', 'datetime', 'timedelta'
        ]

        self.column_types = [
            Number(), Text(), Boolean(), Date(), DateTime(), TimeDelta()
        ]

        self.json_funcs = [c.jsonify for c in self.column_types]

    def test_to_dict(self):
        table = Table(self.rows, self.column_names, self.column_types)

        d1 = table.to_dict('text', column_funcs=self.json_funcs)

        with open('examples/test_keyed.json') as f:
            d2 = json.load(f, object_pairs_hook=OrderedDict)

        self.assertEqual(d1, d2)

    def test_to_dict_func(self):
        table = Table(self.rows, self.column_names, self.column_types)

        key_func = lambda r: r['text']
        d1 = table.to_dict(key_func, column_funcs=self.json_funcs)

        with open('examples/test_keyed.json') as f:
            d2 = json.load(f, object_pairs_hook=OrderedDict)

        self.assertEqual(d1, d2)

