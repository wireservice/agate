#!/usr/bin/env Python

import datetime
from decimal import Decimal
import warnings

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate import Table
from agate.aggregations import *
from agate.data_types import *
from agate.exceptions import *
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
        summary.validate(self.table)
        self.assertEqual(summary.run(self.table), True)

    def test_has_nulls(self):
        has_nulls = HasNulls('one')

        self.assertIsInstance(has_nulls.get_aggregate_data_type(None), Boolean)
        has_nulls.validate(self.table)
        self.assertEqual(has_nulls.run(self.table), True)

    def test_any(self):
        with self.assertRaises(ValueError):
            Any('one').validate(self.table)

        Any('one', lambda d: d).validate(self.table)

        self.assertIsInstance(Any('one').get_aggregate_data_type(None), Boolean)

        self.assertEqual(Any('one', lambda d: d == 2).run(self.table), True)
        self.assertEqual(Any('one', lambda d: d == 5).run(self.table), False)

    def test_all(self):
        with self.assertRaises(ValueError):
            All('one').validate(self.table)

        All('one', lambda d: d).validate(self.table)

        self.assertIsInstance(All('one').get_aggregate_data_type(None), Boolean)
        self.assertEqual(All('one', lambda d: d != 5).run(self.table), True)
        self.assertEqual(All('one', lambda d: d == 2).run(self.table), False)

    def test_count(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.column_names, self.column_types)

        self.assertIsInstance(Count().get_aggregate_data_type(table), Number)
        Count().validate(self.table)
        self.assertEqual(Count().run(table), 5)
        self.assertEqual(Count().run(table), 5)

    def test_count_column(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.column_names, self.column_types)

        self.assertIsInstance(Count('one').get_aggregate_data_type(table), Number)
        Count('one').validate(self.table)
        self.assertEqual(Count('one').run(table), 4)
        self.assertEqual(Count('two').run(table), 5)

    def test_count_value(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = Table(rows, self.column_names, self.column_types)

        self.assertIsInstance(Count('one', 1).get_aggregate_data_type(table), Number)
        Count('one', 1).validate(self.table)
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
        Any('test').validate(table)
        self.assertEqual(Any('test').run(table), True)

        rows = [
            [False],
            [False],
            [None]
        ]

        table = Table(rows, ['test'], [Boolean()])
        Any('test').validate(table)
        self.assertEqual(Any('test').run(table), False)

    def test_all(self):
        rows = [
            [True],
            [True],
            [None]
        ]

        table = Table(rows, ['test'], [Boolean()])
        All('test').validate(table)
        self.assertEqual(All('test').run(table), False)

        rows = [
            [True],
            [True],
            [True]
        ]

        table = Table(rows, ['test'], [Boolean()])
        All('test').validate(table)
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
        Min('test').validate(table)
        self.assertEqual(Min('test').run(table), datetime.datetime(1994, 3, 3, 6, 30))

    def test_max(self):
        rows = [
            [datetime.datetime(1994, 3, 3, 6, 31)],
            [datetime.datetime(1994, 3, 3, 6, 30, 30)],
            [datetime.datetime(1994, 3, 3, 6, 30)],
        ]

        table = Table(rows, ['test'], [DateTime()])

        self.assertIsInstance(Max('test').get_aggregate_data_type(table), DateTime)
        Max('test').validate(table)
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
        with self.assertRaises(DataTypeError):
            MaxPrecision('three').validate(self.table)

        self.assertIsInstance(MaxPrecision('one').get_aggregate_data_type(self.table), Number)
        MaxPrecision('one').validate(self.table)
        self.assertEqual(MaxPrecision('one').run(self.table), 1)
        self.assertEqual(MaxPrecision('two').run(self.table), 2)

    def test_sum(self):
        with self.assertRaises(DataTypeError):
            Sum('three').validate(self.table)

        Sum('one').validate(self.table)

        self.assertEqual(Sum('one').run(self.table), Decimal('6.5'))
        self.assertEqual(Sum('two').run(self.table), Decimal('13.13'))

    def test_min(self):
        with self.assertRaises(DataTypeError):
            Min('three').validate(self.table)

        Min('one').validate(self.table)

        self.assertEqual(Min('one').run(self.table), Decimal('1.1'))
        self.assertEqual(Min('two').run(self.table), Decimal('2.19'))

    def test_max(self):
        with self.assertRaises(DataTypeError):
            Max('three').validate(self.table)

        Max('one').validate(self.table)

        self.assertEqual(Max('one').run(self.table), Decimal('2.7'))
        self.assertEqual(Max('two').run(self.table), Decimal('4.1'))

    def test_mean(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Mean('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Mean('three').validate(self.table)

        Mean('two').validate(self.table)

        self.assertEqual(Mean('two').run(self.table), Decimal('3.2825'))

    def test_mean_with_nulls(self):
        warnings.simplefilter('ignore')

        Mean('one').validate(self.table)

        self.assertAlmostEqual(Mean('one').run(self.table), Decimal('2.16666666'))

    def test_median(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Median('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Median('three').validate(self.table)

        Median('two').validate(self.table)

        self.assertIsInstance(Median('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(Median('two').run(self.table), Decimal('3.42'))

    def test_mode(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Mode('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Mode('three').validate(self.table)

        Mode('two').validate(self.table)

        self.assertIsInstance(Mode('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(Mode('two').run(self.table), Decimal('3.42'))

    def test_iqr(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            IQR('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            IQR('three').validate(self.table)

        IQR('two').validate(self.table)

        self.assertIsInstance(IQR('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(IQR('two').run(self.table), Decimal('0.955'))

    def test_variance(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Variance('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Variance('three').validate(self.table)

        Variance('two').validate(self.table)

        self.assertIsInstance(Variance('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(
            Variance('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.6332')
        )

    def test_population_variance(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            PopulationVariance('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            PopulationVariance('three').validate(self.table)

        PopulationVariance('two').validate(self.table)

        self.assertIsInstance(PopulationVariance('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(
            PopulationVariance('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.4749')
        )

    def test_stdev(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            StDev('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            StDev('three').validate(self.table)

        StDev('two').validate(self.table)

        self.assertIsInstance(StDev('two').get_aggregate_data_type(self.table), Number)
        self.assertAlmostEqual(
            StDev('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.7958')
        )

    def test_population_stdev(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            PopulationStDev('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            PopulationStDev('three').validate(self.table)

        PopulationStDev('two').validate(self.table)

        self.assertIsInstance(PopulationStDev('two').get_aggregate_data_type(self.table), Number)
        self.assertAlmostEqual(
            PopulationStDev('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.6891')
        )

    def test_mad(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            MAD('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            MAD('three').validate(self.table)

        MAD('two').validate(self.table)

        self.assertIsInstance(MAD('two').get_aggregate_data_type(self.table), Number)
        self.assertAlmostEqual(MAD('two').run(self.table), Decimal('0'))

    def test_percentiles(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Percentiles('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Percentiles('three').validate(self.table)

        Percentiles('two').validate(self.table)

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
            Quartiles('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Quartiles('three').validate(self.table)

        Quartiles('two').validate(self.table)

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
            Quintiles('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Quintiles('three').validate(self.table)

        Quintiles('two').validate(self.table)

        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, ['ints'], [self.number_type])

        quintiles = Quintiles('ints').run(table)  # noqa

    def test_deciles(self):
        warnings.simplefilter('error')

        with self.assertRaises(NullCalculationWarning):
            Deciles('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Deciles('three').validate(self.table)

        Deciles('two').validate(self.table)

        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, ['ints'], [self.number_type])

        deciles = Deciles('ints').run(table)  # noqa


class TestTextAggregation(unittest.TestCase):
    def test_max_length(self):
        rows = [
            ['a'],
            ['gobble'],
            ['w']
        ]

        table = Table(rows, ['test'], [Text()])
        MaxLength('test').validate(table)
        self.assertEqual(MaxLength('test').run(table), 6)
        self.assertIsInstance(MaxLength('test').run(table), Decimal)

    def test_max_length_invalid(self):
        rows = [
            [1],
            [2],
            [3]
        ]

        table = Table(rows, ['test'], [Number()])

        with self.assertRaises(DataTypeError):
            MaxLength('test').validate(table)
