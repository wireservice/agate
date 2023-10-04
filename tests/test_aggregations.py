import datetime
import sys
import unittest
import warnings
from decimal import Decimal

from agate import Table
from agate.aggregations import (IQR, MAD, All, Any, Count, Deciles, First, HasNulls, Max, MaxLength, MaxPrecision,
                                Mean, Median, Min, Mode, Percentiles, PopulationStDev, PopulationVariance, Quartiles,
                                Quintiles, StDev, Sum, Summary, Variance)
from agate.data_types import Boolean, DateTime, Number, Text, TimeDelta
from agate.exceptions import DataTypeError
from agate.utils import Quantiles
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
        Any('one', lambda d: d).validate(self.table)

        self.assertIsInstance(Any('one', 2).get_aggregate_data_type(None), Boolean)

        self.assertEqual(Any('one', 2).run(self.table), True)
        self.assertEqual(Any('one', 5).run(self.table), False)

        self.assertEqual(Any('one', lambda d: d == 2).run(self.table), True)
        self.assertEqual(Any('one', lambda d: d == 5).run(self.table), False)

    def test_all(self):
        All('one', lambda d: d).validate(self.table)

        self.assertIsInstance(All('one', 5).get_aggregate_data_type(None), Boolean)
        self.assertEqual(All('one', lambda d: d != 5).run(self.table), True)
        self.assertEqual(All('one', lambda d: d == 2).run(self.table), False)

    def test_first(self):
        with self.assertRaises(ValueError):
            First('one', lambda d: d == 5).validate(self.table)

        First('one', lambda d: d).validate(self.table)

        self.assertIsInstance(First('one').get_aggregate_data_type(self.table), Number)
        self.assertEqual(First('one').run(self.table), 1)
        self.assertEqual(First('one', lambda d: d == 2).run(self.table), 2)
        self.assertEqual(First('one', lambda d: not d).run(self.table), None)

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
        Any('test', True).validate(table)
        self.assertEqual(Any('test', True).run(table), True)

        rows = [
            [False],
            [False],
            [None]
        ]

        table = Table(rows, ['test'], [Boolean()])
        Any('test', True).validate(table)
        self.assertEqual(Any('test', True).run(table), False)
        self.assertEqual(Any('test', lambda r: r).run(table), False)
        self.assertEqual(Any('test', False).run(table), True)
        self.assertEqual(Any('test', lambda r: not r).run(table), True)

    def test_all(self):
        rows = [
            [True],
            [True],
            [None]
        ]

        table = Table(rows, ['test'], [Boolean()])
        All('test', True).validate(table)
        self.assertEqual(All('test', True).run(table), False)

        rows = [
            [True],
            [True],
            [True]
        ]

        table = Table(rows, ['test'], [Boolean()])
        All('test', True).validate(table)
        self.assertEqual(All('test', True).run(table), True)
        self.assertEqual(All('test', lambda r: r).run(table), True)
        self.assertEqual(All('test', False).run(table), False)
        self.assertEqual(All('test', lambda r: not r).run(table), False)


class TestDateTimeAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = [
            [datetime.datetime(1994, 3, 3, 6, 31)],
            [datetime.datetime(1994, 3, 3, 6, 30, 30)],
            [datetime.datetime(1994, 3, 3, 6, 30)],
        ]

        self.table = Table(self.rows, ['test', 'null'], [DateTime(), DateTime()])

        self.time_delta_rows = [
            [datetime.timedelta(seconds=10), datetime.timedelta(seconds=15), None],
            [datetime.timedelta(seconds=20), None, None],
        ]

        self.time_delta_table = Table(
            self.time_delta_rows, ['test', 'mixed', 'null'], [TimeDelta(), TimeDelta(), TimeDelta()]
        )

    def test_min(self):
        self.assertIsInstance(Min('test').get_aggregate_data_type(self.table), DateTime)
        Min('test').validate(self.table)
        self.assertEqual(Min('test').run(self.table), datetime.datetime(1994, 3, 3, 6, 30))

    def test_min_all_nulls(self):
        self.assertIsNone(Min('null').run(self.table))

    def test_min_time_delta(self):
        self.assertIsInstance(Min('test').get_aggregate_data_type(self.time_delta_table), TimeDelta)
        Min('test').validate(self.time_delta_table)
        self.assertEqual(Min('test').run(self.time_delta_table), datetime.timedelta(0, 10))

    def test_max(self):
        self.assertIsInstance(Max('test').get_aggregate_data_type(self.table), DateTime)
        Max('test').validate(self.table)
        self.assertEqual(Max('test').run(self.table), datetime.datetime(1994, 3, 3, 6, 31))

    def test_max_all_nulls(self):
        self.assertIsNone(Max('null').run(self.table))

    def test_max_time_delta(self):
        self.assertIsInstance(Max('test').get_aggregate_data_type(self.time_delta_table), TimeDelta)
        Max('test').validate(self.time_delta_table)
        self.assertEqual(Max('test').run(self.time_delta_table), datetime.timedelta(0, 20))

    def test_mean(self):
        with self.assertWarns(NullCalculationWarning):
            Mean('mixed').validate(self.time_delta_table)

        Mean('test').validate(self.time_delta_table)

        self.assertEqual(Mean('test').run(self.time_delta_table), datetime.timedelta(seconds=15))

    def test_mean_all_nulls(self):
        self.assertIsNone(Mean('null').run(self.time_delta_table))

    def test_mean_with_nulls(self):
        warnings.simplefilter('ignore')

        try:
            Mean('mixed').validate(self.time_delta_table)
        finally:
            warnings.resetwarnings()

        self.assertAlmostEqual(Mean('mixed').run(self.time_delta_table), datetime.timedelta(seconds=15))

    def test_sum(self):
        self.assertIsInstance(Sum('test').get_aggregate_data_type(self.time_delta_table), TimeDelta)
        Sum('test').validate(self.time_delta_table)
        self.assertEqual(Sum('test').run(self.time_delta_table), datetime.timedelta(seconds=30))

    def test_sum_all_nulls(self):
        self.assertEqual(Sum('null').run(self.time_delta_table), datetime.timedelta(0))


class TestNumberAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (Decimal('1.1'), Decimal('2.19'), 'a', None),
            (Decimal('2.7'), Decimal('3.42'), 'b', None),
            (None, Decimal('4.1'), 'c', None),
            (Decimal('2.7'), Decimal('3.42'), 'c', None)
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['one', 'two', 'three', 'four']
        self.column_types = [self.number_type, self.number_type, self.text_type, self.number_type]

        self.table = Table(self.rows, self.column_names, self.column_types)

    def test_max_precision(self):
        with self.assertRaises(DataTypeError):
            MaxPrecision('three').validate(self.table)

        self.assertIsInstance(MaxPrecision('one').get_aggregate_data_type(self.table), Number)
        MaxPrecision('one').validate(self.table)
        self.assertEqual(MaxPrecision('one').run(self.table), 1)
        self.assertEqual(MaxPrecision('two').run(self.table), 2)

    def test_max_precision_all_nulls(self):
        self.assertEqual(MaxPrecision('four').run(self.table), 0)

    def test_sum(self):
        with self.assertRaises(DataTypeError):
            Sum('three').validate(self.table)

        Sum('one').validate(self.table)

        self.assertEqual(Sum('one').run(self.table), Decimal('6.5'))
        self.assertEqual(Sum('two').run(self.table), Decimal('13.13'))

    def test_sum_all_nulls(self):
        self.assertEqual(Sum('four').run(self.table), Decimal('0'))

    def test_min(self):
        with self.assertRaises(DataTypeError):
            Min('three').validate(self.table)

        Min('one').validate(self.table)

        self.assertEqual(Min('one').run(self.table), Decimal('1.1'))
        self.assertEqual(Min('two').run(self.table), Decimal('2.19'))

    def test_min_all_nulls(self):
        self.assertIsNone(Min('four').run(self.table))

    def test_max(self):
        with self.assertRaises(DataTypeError):
            Max('three').validate(self.table)

        Max('one').validate(self.table)

        self.assertEqual(Max('one').run(self.table), Decimal('2.7'))
        self.assertEqual(Max('two').run(self.table), Decimal('4.1'))

    def test_max_all_nulls(self):
        self.assertIsNone(Max('four').run(self.table))

    def test_mean(self):
        with self.assertWarns(NullCalculationWarning):
            Mean('one').validate(self.table)

        Mean('two').validate(self.table)

        with self.assertRaises(DataTypeError):
            Mean('three').validate(self.table)

        self.assertEqual(Mean('two').run(self.table), Decimal('3.2825'))

    def test_mean_all_nulls(self):
        self.assertIsNone(Mean('four').run(self.table))

    def test_mean_with_nulls(self):
        warnings.simplefilter('ignore')

        try:
            Mean('one').validate(self.table)
        finally:
            warnings.resetwarnings()

        self.assertAlmostEqual(Mean('one').run(self.table), Decimal('2.16666666'))

    def test_median(self):
        with self.assertWarns(NullCalculationWarning):
            Median('one').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            with self.assertRaises(DataTypeError):
                Median('three').validate(self.table)
        finally:
            warnings.resetwarnings()

        Median('two').validate(self.table)

        self.assertIsInstance(Median('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(Median('two').run(self.table), Decimal('3.42'))

    def test_median_all_nulls(self):
        self.assertIsNone(Median('four').run(self.table))

    def test_mode(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                Mode('one').validate(self.table)

            with self.assertRaises(DataTypeError):
                Mode('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            Mode('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        self.assertIsInstance(Mode('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(Mode('two').run(self.table), Decimal('3.42'))

    def test_mode_all_nulls(self):
        self.assertIsNone(Mode('four').run(self.table))

    def test_iqr(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                IQR('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            IQR('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            IQR('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        self.assertIsInstance(IQR('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(IQR('two').run(self.table), Decimal('0.955'))

    def test_irq_all_nulls(self):
        self.assertIsNone(IQR('four').run(self.table))

    def test_variance(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                Variance('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Variance('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            Variance('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        self.assertIsInstance(Variance('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(
            Variance('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.6332')
        )

    def test_variance_all_nulls(self):
        self.assertIsNone(Variance('four').run(self.table))

    def test_population_variance(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                PopulationVariance('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            PopulationVariance('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            PopulationVariance('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        self.assertIsInstance(PopulationVariance('two').get_aggregate_data_type(self.table), Number)
        self.assertEqual(
            PopulationVariance('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.4749')
        )

    def test_population_variance_all_nulls(self):
        self.assertIsNone(PopulationVariance('four').run(self.table))

    def test_stdev(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                StDev('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            StDev('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            StDev('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        self.assertIsInstance(StDev('two').get_aggregate_data_type(self.table), Number)
        self.assertAlmostEqual(
            StDev('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.7958')
        )

    def test_stdev_all_nulls(self):
        self.assertIsNone(StDev('four').run(self.table))

    def test_population_stdev(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                PopulationStDev('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            PopulationStDev('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            PopulationStDev('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        self.assertIsInstance(PopulationStDev('two').get_aggregate_data_type(self.table), Number)
        self.assertAlmostEqual(
            PopulationStDev('two').run(self.table).quantize(Decimal('0.0001')),
            Decimal('0.6891')
        )

    def test_population_stdev_all_nulls(self):
        self.assertIsNone(PopulationStDev('four').run(self.table))

    def test_mad(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                MAD('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            MAD('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            MAD('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        self.assertIsInstance(MAD('two').get_aggregate_data_type(self.table), Number)
        self.assertAlmostEqual(MAD('two').run(self.table), Decimal('0'))

    def test_mad_all_nulls(self):
        self.assertIsNone(MAD('four').run(self.table))

    def test_percentiles(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                Percentiles('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Percentiles('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            Percentiles('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, ['ints'], [self.number_type])

        percentiles = Percentiles('ints').run(table)

        self.assertEqual(percentiles[0], Decimal('1'))
        self.assertEqual(percentiles[25], Decimal('250.5'))
        self.assertEqual(percentiles[50], Decimal('500.5'))
        self.assertEqual(percentiles[75], Decimal('750.5'))
        self.assertEqual(percentiles[99], Decimal('990.5'))
        self.assertEqual(percentiles[100], Decimal('1000'))

    def test_percentiles_all_nulls(self):
        self.assertEqual(Percentiles('four').run(self.table), Quantiles([None] * 101))

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
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                Quartiles('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Quartiles('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            Quartiles('two').validate(self.table)
        finally:
            warnings.resetwarnings()

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

    def test_quartiles_all_nulls(self):
        self.assertEqual(Quartiles('four').run(self.table), Quantiles([None] * 5))

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
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                Quintiles('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Quintiles('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            Quintiles('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        rows = [(n,) for n in range(1, 1000)]

        table = Table(rows, ['ints'], [self.number_type])

        quintiles = Quintiles('ints').run(table)
        for i, v in enumerate(['1', '200', '400', '600', '800', '999']):
            self.assertEqual(quintiles[i], Decimal(v))

    def test_quintiles_all_nulls(self):
        self.assertEqual(Quintiles('four').run(self.table), Quantiles([None] * 6))

    def test_deciles(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')

            with self.assertRaises(NullCalculationWarning):
                Deciles('one').validate(self.table)

        with self.assertRaises(DataTypeError):
            Deciles('three').validate(self.table)

        warnings.simplefilter('ignore')

        try:
            Deciles('two').validate(self.table)
        finally:
            warnings.resetwarnings()

        rows = [(n,) for n in range(1, 1000)]

        table = Table(rows, ['ints'], [self.number_type])

        deciles = Deciles('ints').run(table)
        for i, v in enumerate(['1', '100', '200', '300', '400', '500', '600', '700', '800', '900', '999']):
            self.assertEqual(deciles[i], Decimal(v))

    def test_deciles_all_nulls(self):
        self.assertEqual(Deciles('four').run(self.table), Quantiles([None] * 11))


class TestTextAggregation(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ['a', None],
            ['gobble', None],
            ['w', None]
        ]

        self.table = Table(self.rows, ['test', 'null'], [Text(), Text()])

    def test_max_length(self):
        MaxLength('test').validate(self.table)
        self.assertEqual(MaxLength('test').run(self.table), 6)
        self.assertIsInstance(MaxLength('test').run(self.table), Decimal)

    def test_max_length_all_nulls(self):
        self.assertEqual(MaxLength('null').run(self.table), 0)

    def test_max_length_unicode(self):
        """
        This text documents different handling of wide-unicode characters in
        Python 2 and Python 3. The former's behavior is broken, but can not
        be easily fixed.

        Bug: https://github.com/wireservice/agate/issues/649
        Reference: http://stackoverflow.com/a/35462951
        """
        rows = [
            ['a'],
            ['👍'],
            ['w']
        ]

        table = Table(rows, ['test'], [Text()])

        MaxLength('test').validate(table)

        # Non 4-byte versions of Python 2 (but not PyPy)
        if sys.maxunicode <= 65535:
            self.assertEqual(MaxLength('test').run(table), 2)
        # Modern versions of Python
        else:
            self.assertEqual(MaxLength('test').run(table), 1)

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
