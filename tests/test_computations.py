import datetime
import unittest
import warnings
from decimal import Decimal

from agate import Table
from agate.computations import Change, Formula, Percent, PercentChange, PercentileRank, Rank, Slug
from agate.data_types import Boolean, Date, DateTime, Number, Text, TimeDelta
from agate.exceptions import CastError, DataTypeError
from agate.warns import NullCalculationWarning


class TestTableComputation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            ('a', 2, 3, 4),
            (None, 3, 5, None),
            ('a', 2, 4, None),
            ('b', 3, 4, None)
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = [
            'one', 'two', 'three', 'four'
        ]
        self.column_types = [
            self.text_type, self.number_type, self.number_type, self.number_type
        ]

        self.table = Table(self.rows, self.column_names, self.column_types)

    def test_formula(self):
        new_table = self.table.compute([
            ('test', Formula(self.number_type, lambda r: r['two'] + r['three']))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', Decimal('2'), Decimal('3'), Decimal('4'), Decimal('5')))
        self.assertEqual(new_table.columns['test'][0], Decimal('5'))
        self.assertEqual(new_table.columns['test'][1], Decimal('8'))
        self.assertEqual(new_table.columns['test'][2], Decimal('6'))
        self.assertEqual(new_table.columns['test'][3], Decimal('7'))

    def test_formula_invalid(self):
        with self.assertRaises(CastError):
            self.table.compute([
                ('test', Formula(self.number_type, lambda r: r['one']))
            ])

    def test_formula_no_validate(self):
        new_table = self.table.compute([
            ('test', Formula(self.number_type, lambda r: r['one'], cast=False))
        ])

        # Now everything is screwed up
        self.assertSequenceEqual(new_table.rows[0], ('a', Decimal('2'), Decimal('3'), Decimal('4'), 'a'))
        self.assertEqual(new_table.columns['test'][0], 'a')

    def test_change(self):
        new_table = self.table.compute([
            ('test', Change('two', 'three'))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', Decimal('2'), Decimal('3'), Decimal('4'), Decimal('1')))
        self.assertEqual(new_table.columns['test'][0], Decimal('1'))
        self.assertEqual(new_table.columns['test'][1], Decimal('2'))
        self.assertEqual(new_table.columns['test'][2], Decimal('2'))
        self.assertEqual(new_table.columns['test'][3], Decimal('1'))

    def test_change_mixed_types(self):
        rows = (
            ('1', '10/24/1978'),
            ('2', '11/13/1974')
        )

        column_names = ['number', 'date']
        column_types = [Number(), Date()]

        table = Table(rows, column_names, column_types)

        with self.assertRaises(DataTypeError):
            table.compute([
                ('test', Change('number', 'date'))
            ])

    def test_changed_invalid_types(self):
        rows = (
            (False, True),
            (True, False)
        )

        column_names = ['before', 'after']
        column_types = [Boolean(), Boolean()]

        table = Table(rows, column_names, column_types)

        with self.assertRaises(DataTypeError):
            table.compute([
                ('test', Change('before', 'after'))
            ])

    def test_change_nulls(self):
        with self.assertWarns(NullCalculationWarning):
            new_table = self.table.compute([
                ('test', Change('three', 'four'))
            ])

        with self.assertWarns(NullCalculationWarning):
            new_table = self.table.compute([
                ('test', Change('four', 'three'))
            ])

        warnings.simplefilter('ignore')

        try:
            new_table = self.table.compute([
                ('test', Change('three', 'four'))
            ])
        finally:
            warnings.resetwarnings()

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', Decimal('2'), Decimal('3'), Decimal('4'), Decimal('1')))
        self.assertEqual(new_table.columns['test'][0], Decimal('1'))
        self.assertEqual(new_table.columns['test'][1], None)
        self.assertEqual(new_table.columns['test'][2], None)
        self.assertEqual(new_table.columns['test'][3], None)

    def test_percent(self):
        new_table = self.table.compute([
            ('test', Percent('two'))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        def to_one_place(d):
            return d.quantize(Decimal('0.1'))

        self.assertSequenceEqual(
            new_table.rows[0],
            ('a', Decimal('2'), Decimal('3'), Decimal('4'), Decimal('20.0'))
        )
        self.assertEqual(to_one_place(new_table.columns['test'][0]), Decimal('20.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][1]), Decimal('30.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][2]), Decimal('20.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][3]), Decimal('30.0'))

    def test_percent_total_override(self):
        new_table = self.table.compute([
            ('test', Percent('two', 5))
        ])

        def to_one_place(d):
            return d.quantize(Decimal('0.1'))

        self.assertEqual(to_one_place(new_table.columns['test'][0]), Decimal('40.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][1]), Decimal('60.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][2]), Decimal('40.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][3]), Decimal('60.0'))

        with self.assertRaises(DataTypeError):
            self.table.compute([
                ('test', Percent('two', 0))
            ])
        with self.assertRaises(DataTypeError):
            self.table.compute([
                ('test', Percent('two', -1))
            ])
        with self.assertRaises(DataTypeError):
            zero_table = Table([[0]], ['zero'], [self.number_type])
            new_table = zero_table.compute([('test', Percent('zero'))])

    def test_percent_zeros(self):
        column_names = ['label', 'value']
        rows = (
            ('one', 25),
            ('two', 25),
            ('three', 0)
        )
        new_table = Table(rows, column_names)
        new_table = new_table.compute([
            ('test', Percent('value')),
        ])

        def to_one_place(d):
            return d.quantize(Decimal('0.1'))

        self.assertEqual(to_one_place(new_table.columns['test'][0]), Decimal('50.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][1]), Decimal('50.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][2]), Decimal('0.0'))

    def test_percent_nulls(self):
        warnings.simplefilter('ignore')

        try:
            new_table = self.table.compute([
                ('test', Percent('four'))
            ])
        finally:
            warnings.resetwarnings()

        def to_one_place(d):
            return d.quantize(Decimal('0.1'))

        self.assertEqual(
            to_one_place(new_table.columns['test'][0]),
            Decimal('100.0')
        )
        self.assertEqual(new_table.columns['test'][1], None)
        self.assertEqual(new_table.columns['test'][2], None)
        self.assertEqual(new_table.columns['test'][3], None)

    def test_percent_change(self):
        new_table = self.table.compute([
            ('test', PercentChange('two', 'three'))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        def to_one_place(d):
            return d.quantize(Decimal('0.1'))

        self.assertSequenceEqual(new_table.rows[0], ('a', Decimal('2'), Decimal('3'), Decimal('4'), Decimal('50.0')))
        self.assertEqual(to_one_place(new_table.columns['test'][0]), Decimal('50.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][1]), Decimal('66.7'))
        self.assertEqual(to_one_place(new_table.columns['test'][2]), Decimal('100.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][3]), Decimal('33.3'))

    def test_percent_change_invalid_columns(self):
        with self.assertRaises(DataTypeError):
            self.table.compute([
                ('test', PercentChange('one', 'three'))
            ])

        with self.assertRaises(DataTypeError):
            self.table.compute([
                ('test', PercentChange('three', 'one'))
            ])

    def test_percent_change_nulls(self):
        with self.assertWarns(NullCalculationWarning):
            new_table = self.table.compute([
                ('test', PercentChange('three', 'four'))
            ])

        with self.assertWarns(NullCalculationWarning):
            new_table = self.table.compute([
                ('test', PercentChange('four', 'three'))
            ])

        warnings.simplefilter('ignore')

        try:
            new_table = self.table.compute([
                ('test', PercentChange('three', 'four'))
            ])
        finally:
            warnings.resetwarnings()

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        def to_one_place(d):
            return d.quantize(Decimal('0.1'))

        self.assertSequenceEqual(new_table.rows[2], ('a', Decimal('2'), Decimal('4'), None, None))
        self.assertEqual(to_one_place(new_table.columns['test'][0]), Decimal('33.3'))
        self.assertEqual(new_table.columns['test'][1], None)
        self.assertEqual(new_table.columns['test'][2], None)
        self.assertEqual(new_table.columns['test'][3], None)

    def test_rank_number(self):
        new_table = self.table.compute([
            ('rank', Rank('two'))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)
        self.assertSequenceEqual(new_table.columns['rank'], (1, 3, 1, 3))
        self.assertIsInstance(new_table.columns['rank'][0], Decimal)

    def test_rank_number_reverse(self):
        new_table = self.table.compute([
            ('rank', Rank('two', reverse=True))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)
        self.assertSequenceEqual(new_table.columns['rank'], (3, 1, 3, 1))

    def test_rank_number_key(self):
        new_table = self.table.compute([
            ('rank', Rank('two', comparer=lambda x, y: int(y - x)))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)
        self.assertSequenceEqual(new_table.columns['rank'], (3, 1, 3, 1))

    def test_rank_number_reverse_key(self):
        new_table = self.table.compute([
            ('rank', Rank('two', comparer=lambda x, y: int(y - x), reverse=True))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)
        self.assertSequenceEqual(new_table.columns['rank'], (1, 3, 1, 3))

    def test_rank_text(self):
        new_table = self.table.compute([
            ('rank', Rank('one'))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)
        self.assertSequenceEqual(new_table.columns['rank'], (1, 4, 1, 3))

    def test_percentile_rank(self):
        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, ['ints'], [self.number_type])
        new_table = table.compute([
            ('percentiles', PercentileRank('ints'))
        ])

        self.assertEqual(len(new_table.rows), 1000)
        self.assertEqual(len(new_table.columns), 2)

        self.assertSequenceEqual(new_table.rows[0], (1, 0))
        self.assertSequenceEqual(new_table.rows[50], (51, 5))
        self.assertSequenceEqual(new_table.rows[499], (500, 49))
        self.assertSequenceEqual(new_table.rows[500], (501, 50))
        self.assertSequenceEqual(new_table.rows[998], (999, 99))
        self.assertSequenceEqual(new_table.rows[999], (1000, 100))
        self.assertIsInstance(new_table.columns['percentiles'][0], Decimal)
        self.assertIsInstance(new_table.columns['percentiles'][-1], Decimal)

    def test_percentile_rank_invalid_types(self):
        with self.assertRaises(DataTypeError):
            self.table.compute([
                ('test', PercentileRank('one'))
            ])

    def test_slug(self):
        rows = (
            ('hello world', 2),
            ('Ab*c #e', 2),
            ('He11O W0rld', 3)
        )
        expected = ['hello_world', 'ab_c_e', 'he11o_w0rld']

        table = Table(rows, ['one', 'two'], [self.text_type, self.number_type]).compute([
            ('slugs', Slug('one'))
        ])

        self.assertSequenceEqual(table.columns['slugs'], expected)

    def test_slug_column_name_sequence(self):
        rows = (
            ('hello world', 2, 'Ab*c #e'),
            ('Ab*c #e', 2, 'He11O W0rld'),
            ('He11O W0rld', 3, 'hello world')
        )
        expected = ['hello_world_ab_c_e', 'ab_c_e_he11o_w0rld', 'he11o_w0rld_hello_world']

        table1 = Table(rows, ['one', 'two', 'three'], [self.text_type, self.number_type, self.text_type])
        table2 = table1.compute([
            ('slugs', Slug(['one', 'three']))
        ])

        self.assertSequenceEqual(table2.columns['slugs'], expected)

    def test_slug_ensure_unique(self):
        rows = (
            ('hello world', 2),
            ('Ab*c #e', 2),
            ('He11O W0rld', 3),
            ('HellO WOrld ', 3)
        )
        expected = ['hello_world', 'ab_c_e', 'he11o_w0rld', 'hello_world_2']

        table = Table(rows, ['one', 'two'], [self.text_type, self.number_type]).compute([
            ('slugs', Slug('one', ensure_unique=True))
        ])

        self.assertSequenceEqual(table.columns['slugs'], expected)

    def test_slug_contains_null_error(self):
        with self.assertRaises(ValueError):
            self.table.compute([
                ('slugs', Slug('one', ensure_unique=True))
            ])


class TestDateAndTimeComputations(unittest.TestCase):
    def test_change_dates(self):
        rows = (
            ('10/4/2015', '10/7/2015'),
            ('10/2/2015', '9/28/2015'),
            ('9/28/2015', '9/1/2015')
        )

        date_type = Date()

        column_names = ['one', 'two']
        column_types = [date_type, date_type]

        table = Table(rows, column_names, column_types)

        new_table = table.compute([
            ('test', Change('one', 'two'))
        ])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)

        self.assertSequenceEqual(new_table.rows[0], (
            datetime.date(2015, 10, 4),
            datetime.date(2015, 10, 7),
            datetime.timedelta(days=3)
        ))

        self.assertEqual(new_table.columns['test'][0], datetime.timedelta(days=3))
        self.assertEqual(new_table.columns['test'][1], datetime.timedelta(days=-4))
        self.assertEqual(new_table.columns['test'][2], datetime.timedelta(days=-27))

    def test_change_datetimes(self):
        rows = (
            ('10/4/2015 4:43', '10/7/2015 4:50'),
            ('10/2/2015 12 PM', '9/28/2015 12 PM'),
            ('9/28/2015 12:00:00', '9/1/2015 6 PM')
        )

        datetime_type = DateTime()

        column_names = ['one', 'two']
        column_types = [datetime_type, datetime_type]

        table = Table(rows, column_names, column_types)

        new_table = table.compute([
            ('test', Change('one', 'two'))
        ])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)

        self.assertSequenceEqual(new_table.rows[0], (
            datetime.datetime(2015, 10, 4, 4, 43),
            datetime.datetime(2015, 10, 7, 4, 50),
            datetime.timedelta(days=3, minutes=7)
        ))

        self.assertEqual(new_table.columns['test'][0], datetime.timedelta(days=3, minutes=7))
        self.assertEqual(new_table.columns['test'][1], datetime.timedelta(days=-4))
        self.assertEqual(new_table.columns['test'][2], datetime.timedelta(days=-26, hours=-18))

    def test_change_timedeltas(self):
        rows = (
            ('4:15', '8:18'),
            ('4h 2m', '2h'),
            ('4 weeks', '27 days')
        )

        timedelta_type = TimeDelta()

        column_names = ['one', 'two']
        column_types = [timedelta_type, timedelta_type]

        table = Table(rows, column_names, column_types)

        new_table = table.compute([
            ('test', Change('one', 'two'))
        ])

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.rows), 3)
        self.assertEqual(len(new_table.columns), 3)

        self.assertSequenceEqual(new_table.rows[0], (
            datetime.timedelta(minutes=4, seconds=15),
            datetime.timedelta(minutes=8, seconds=18),
            datetime.timedelta(minutes=4, seconds=3)
        ))
        self.assertEqual(new_table.columns['test'][0], datetime.timedelta(minutes=4, seconds=3))
        self.assertEqual(new_table.columns['test'][1], datetime.timedelta(hours=-2, minutes=-2))
        self.assertEqual(new_table.columns['test'][2], datetime.timedelta(days=-1))
