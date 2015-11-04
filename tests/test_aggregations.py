#!/usr/bin/env Python

import datetime
from decimal import Decimal
import warnings

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import Mock
except:
    from mock import Mock

from agate import Table
from agate.aggregations import *
from agate.columns import Column
from agate.data_types import *
from agate.exceptions import *
from agate.rows import Row
from agate.warns import NullCalculationWarning

class TestSimpleAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

        self.table = Table(self.rows, self.column_names, self.column_types)

    def test_summary(self):
        summary = Summary('one', Boolean(), lambda c: 2 in c)

        self.assertIsInstance(summary.get_aggregate_data_type(None), Boolean)
        self.assertEqual(summary.run(self.table), True)

    def test_any(self):
        with self.assertRaises(ValueError):
            Any('one').run(self.table)

        self.assertIsInstance(Any('one').get_aggregate_data_type(None), Boolean)
        self.assertEqual(Any('one', lambda d: d == 2).run(self.table), True)
        self.assertEqual(Any('one', lambda d: d == 5).run(self.table), False)

    def test_all(self):
        with self.assertRaises(ValueError):
            All('one').run(self.table)

        self.assertIsInstance(All('one').get_aggregate_data_type(None), Boolean)
        self.assertEqual(All('one', lambda d: d != 5).run(self.table), True)
        self.assertEqual(All('one', lambda d: d == 2).run(self.table), False)

    def test_length(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.column_names, self.column_types)

        self.assertEqual(Length().run(table), 5)
        self.assertEqual(Length().run(table), 5)

    def test_count(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.column_names, self.column_types)

        self.assertEqual(Count('one', 1).run(table), 3)
        self.assertEqual(Count('one', 4).run(table), 0)
        self.assertEqual(Count('one', None).run(table), 1)

class TestBooleanAggregation(unittest.TestCase):
    def test_any(self):
        rows = [
            [True],
            [False],
            [None]
        ]

        table = Table(rows, ['test'], [Boolean()])
        self.assertEqual(Any('test').run(table), True)

        rows = [
            [False],
            [False],
            [None]
        ]

        table = Table(rows, ['test'], [Boolean()])
        self.assertEqual(Any('test').run(table), False)

    def test_all(self):
        rows = [
            [True],
            [True],
            [None]
        ]

        table = Table(rows, ['test'], [Boolean()])
        self.assertEqual(All('test').run(table), False)

        rows = [
            [True],
            [True],
            [True]
        ]

        table = Table(rows, ['test'], [Boolean()])
        self.assertEqual(All('test').run(table), True)

class TestDateTimeAggregation(unittest.TestCase):
    def test_min(self):
        rows = [
            [datetime.datetime(1994, 3, 3, 6, 31)],
            [datetime.datetime(1994, 3, 3, 6, 30, 30)],
            [datetime.datetime(1994, 3, 3, 6, 30)],
        ]

        table = Table(rows, ['test'], [DateTime()])

        self.assertIsInstance(Min('test').get_aggregate_data_type(table), DateTime)
        self.assertEqual(Min('test').run(table), datetime.datetime(1994, 3, 3, 6, 30))

    def test_max(self):
        rows = [
            [datetime.datetime(1994, 3, 3, 6, 31)],
            [datetime.datetime(1994, 3, 3, 6, 30, 30)],
            [datetime.datetime(1994, 3, 3, 6, 30)],
        ]

        table = Table(rows, ['test'], [DateTime()])

        self.assertIsInstance(Max('test').get_aggregate_data_type(table), DateTime)
        self.assertEqual(Max('test').run(table), datetime.datetime(1994, 3, 3, 6, 31))

class TestNumberAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (Decimal('1.1'), Decimal('2.19'), 'a'),
            (Decimal('2.7'), Decimal('3.42'), 'b'),
            (None, Decimal('4.1'), 'c'),
            (Decimal('2.7'), Decimal('3.42'), 'c')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three']
        self.column_types = [self.number_type, self.number_type, self.text_type]

        self.table = Table(self.rows, self.column_names, self.column_types)

    def test_max_precision(self):
        self.assertEqual(MaxPrecision('one').run(self.table), 1)
        self.assertEqual(MaxPrecision('two').run(self.table), 2)

        with self.assertRaises(DataTypeError):
            MaxPrecision('three').run(self.table)

    def test_sum(self):
        self.assertEqual(Sum('one').run(self.table), Decimal('6.5'))
        self.assertEqual(Sum('two').run(self.table), Decimal('13.13'))

        with self.assertRaises(DataTypeError):
            Sum('three').run(self.table)

    def test_min(self):
        with self.assertRaises(DataTypeError):
            Min('three').run(self.table)

        self.assertEqual(Min('one').run(self.table), Decimal('1.1'))
        self.assertEqual(Min('two').run(self.table), Decimal('2.19'))

    def test_max(self):
        with self.assertRaises(DataTypeError):
            Max('three').run(self.table)

        self.assertEqual(Max('one').run(self.table), Decimal('2.7'))
        self.assertEqual(Max('two').run(self.table), Decimal('4.1'))

    def test_mean(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Mean('one').run(self.table)

        with self.assertRaises(DataTypeError):
            Mean('three').run(self.table)

        self.assertEqual(Mean('two').run(self.table), Decimal('3.2825'))

    def test_mean_with_nulls(self):
        warnings.simplefilter('ignore')

        self.assertAlmostEqual(Mean('one').run(self.table), Decimal('2.16666666'))

    def test_median(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Median('one').run(self.table)

        with self.assertRaises(DataTypeError):
            Median('three').run(self.table)

        self.assertEqual(Median('two').run(self.table), Decimal('3.42'))

    def test_mode(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Mode('one').run(self.table)

        with self.assertRaises(DataTypeError):
            Mode('three').run(self.table)

        self.assertEqual(Mode('two').run(self.table), Decimal('3.42'))

    def test_iqr(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            IQR('one').run(self.table)

        with self.assertRaises(DataTypeError):
            IQR('three').run(self.table)

        self.assertEqual(IQR('two').run(self.table), Decimal('0.955'))

    def test_variance(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Variance('one').run(self.table)

        with self.assertRaises(DataTypeError):
            Variance('three').run(self.table)

        self.assertEqual(
            Variance('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.6332')
        )

    def test_population_variance(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            PopulationVariance('one').run(self.table)

        with self.assertRaises(DataTypeError):
            PopulationVariance('three').run(self.table)

        self.assertEqual(
            PopulationVariance('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.4749')
        )

    def test_stdev(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            StDev('one').run(self.table)

        with self.assertRaises(DataTypeError):
            StDev('three').run(self.table)

        self.assertAlmostEqual(
            StDev('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.7958')
        )

    def test_population_stdev(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            PopulationStDev('one').run(self.table)

        with self.assertRaises(DataTypeError):
            PopulationStDev('three').run(self.table)

        self.assertAlmostEqual(
            PopulationStDev('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.6891')
        )

    def test_mad(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            MAD('one').run(self.table)

        with self.assertRaises(DataTypeError):
            MAD('three').run(self.table)

        self.assertAlmostEqual(MAD('two').run(self.table), Decimal('0'))

    def test_percentiles(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Percentiles('one').run(self.table)

        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, ['ints'], [self.number_type])

        percentiles = Percentiles('ints').run(table)

        self.assertEqual(percentiles[0], Decimal('1'))
        self.assertEqual(percentiles[25], Decimal('250.5'))
        self.assertEqual(percentiles[50], Decimal('500.5'))
        self.assertEqual(percentiles[75], Decimal('750.5'))
        self.assertEqual(percentiles[99], Decimal('990.5'))
        self.assertEqual(percentiles[100], Decimal('1000'))

    def test_percentiles_locate(self):
        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, ['ints'], [self.number_type])

        percentiles = Percentiles('ints').run(table)

        self.assertEqual(percentiles.locate(251), Decimal('25'))
        self.assertEqual(percentiles.locate(260), Decimal('25'))
        self.assertEqual(percentiles.locate(261), Decimal('26'))

        with self.assertRaises(ValueError):
            percentiles.locate(0)

        with self.assertRaises(ValueError):
            percentiles.locate(1012)

    def test_quartiles(self):
        """
        CDF quartile tests from:
        http://www.amstat.org/publications/jse/v14n3/langford.html#Parzen1979
        """
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Quartiles('one').run(self.table)

        # N = 4
        rows = [(n,) for n in [1, 2, 3, 4]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        for i, v in enumerate(['1', '1.5', '2.5', '3.5', '4']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 5
        rows = [(n,) for n in [1, 2, 3, 4, 5]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        for i, v in enumerate(['1', '2', '3', '4', '5']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 6
        rows = [(n,) for n in [1, 2, 3, 4, 5, 6]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        for i, v in enumerate(['1', '2', '3.5', '5', '6']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 7
        rows = [(n,) for n in [1, 2, 3, 4, 5, 6, 7]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        for i, v in enumerate(['1', '2', '4', '6', '7']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 8 (doubled)
        rows = [(n,) for n in [1, 1, 2, 2, 3, 3, 4, 4]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        for i, v in enumerate(['1', '1.5', '2.5', '3.5', '4']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 10 (doubled)
        rows = [(n,) for n in [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        for i, v in enumerate(['1', '2', '3', '4', '5']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 12 (doubled)
        rows = [(n,) for n in [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        for i, v in enumerate(['1', '2', '3.5', '5', '6']):
            self.assertEqual(quartiles[i], Decimal(v))

        # N = 14 (doubled)
        rows = [(n,) for n in [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        for i, v in enumerate(['1', '2', '4', '6', '7']):
            self.assertEqual(quartiles[i], Decimal(v))

    def test_quartiles_locate(self):
        """
        CDF quartile tests from:
        http://www.amstat.org/publications/jse/v14n3/langford.html#Parzen1979
        """
        # N = 4
        rows = [(n,) for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]

        table = Table(rows, ['ints'], [self.number_type])

        quartiles = Quartiles('ints').run(table)

        self.assertEqual(quartiles.locate(2), Decimal('0'))
        self.assertEqual(quartiles.locate(4), Decimal('1'))
        self.assertEqual(quartiles.locate(6), Decimal('2'))
        self.assertEqual(quartiles.locate(8), Decimal('3'))

        with self.assertRaises(ValueError):
            quartiles.locate(0)

        with self.assertRaises(ValueError):
            quartiles.locate(11)

    def test_quintiles(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Quintiles('one').run(self.table)

        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, ['ints'], [self.number_type])

        quintiles = Quintiles('ints').run(table)

    def test_deciles(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Deciles('one').run(self.table)

        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, ['ints'], [self.number_type])

        deciles = Deciles('ints').run(table)

class TestTextAggregation(unittest.TestCase):
    def test_max_length(self):
        rows = [
            ['a'],
            ['gobble'],
            ['w']
        ]

        table = Table(rows, ['test'], [Text()])
        self.assertEqual(MaxLength('test').run(table), 6)

    def test_max_length_invalid(self):
        rows = [
            [1],
            [2],
            [3]
        ]

        table = Table(rows, ['test'], [Number()])

        with self.assertRaises(DataTypeError):
            MaxLength('test').run(table)
