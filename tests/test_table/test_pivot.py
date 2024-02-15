import sys
from decimal import Decimal

from agate import Table
from agate.aggregations import Sum
from agate.computations import Percent
from agate.data_types import Number, Text
from agate.testcase import AgateTestCase


class TestPivot(AgateTestCase):
    def setUp(self):
        self.rows = (
            ('joe', 'white', 'male', 20, 'blue'),
            ('jane', 'white', 'female', 20, 'blue'),
            ('josh', 'black', 'male', 20, 'blue'),
            ('jim', 'latino', 'male', 25, 'blue'),
            ('julia', 'white', 'female', 25, 'green'),
            ('joan', 'asian', 'female', 25, 'green')
        )

        self.number_type = Number()
        self.text_type = Text()

        self.column_names = ['name', 'race', 'gender', 'age', 'color']
        self.column_types = [self.text_type, self.text_type, self.text_type, self.number_type, self.text_type]

    def test_pivot(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot('race', 'gender')

        pivot_rows = (
            ('white', 1, 2),
            ('black', 1, 0),
            ('latino', 1, 0),
            ('asian', 0, 1)
        )

        self.assertColumnNames(pivot_table, ['race', 'male', 'female'])
        self.assertRowNames(pivot_table, ['white', 'black', 'latino', 'asian'])
        self.assertColumnTypes(pivot_table, [Text, Number, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_by_lambda(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot(lambda r: r['gender'])

        pivot_rows = (
            ('male', 3),
            ('female', 3)
        )

        self.assertColumnNames(pivot_table, ['group', 'Count'])
        self.assertRowNames(pivot_table, ['male', 'female'])
        self.assertColumnTypes(pivot_table, [Text, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_by_lambda_group_name(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot(lambda r: r['gender'], key_name='gender')

        pivot_rows = (
            ('male', 3),
            ('female', 3)
        )

        self.assertColumnNames(pivot_table, ['gender', 'Count'])
        self.assertRowNames(pivot_table, ['male', 'female'])
        self.assertColumnTypes(pivot_table, [Text, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_by_lambda_group_name_sequence_invalid(self):
        table = Table(self.rows, self.column_names, self.column_types)

        with self.assertRaises(ValueError):
            table.pivot(['race', 'gender'], key_name='foo')

    def test_pivot_no_key(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot(pivot='gender')

        pivot_rows = (
            (3, 3),
        )

        self.assertColumnNames(pivot_table, ['male', 'female'])
        self.assertColumnTypes(pivot_table, [Number, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_no_pivot(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot('race')

        pivot_rows = (
            ('white', 3),
            ('black', 1),
            ('latino', 1),
            ('asian', 1)
        )

        self.assertColumnNames(pivot_table, ['race', 'Count'])
        self.assertColumnTypes(pivot_table, [Text, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_sum(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot('race', 'gender', Sum('age'))

        pivot_rows = (
            ('white', 20, 45),
            ('black', 20, 0),
            ('latino', 25, 0),
            ('asian', 0, 25)
        )

        self.assertColumnNames(pivot_table, ['race', 'male', 'female'])
        self.assertColumnTypes(pivot_table, [Text, Number, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_multiple_keys(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot(['race', 'gender'], 'age')

        pivot_rows = (
            ('white', 'male', 1, 0),
            ('white', 'female', 1, 1),
            ('black', 'male', 1, 0),
            ('latino', 'male', 0, 1),
            ('asian', 'female', 0, 1),
        )

        self.assertRows(pivot_table, pivot_rows)
        self.assertColumnNames(pivot_table, ['race', 'gender', '20', '25'])
        self.assertRowNames(pivot_table, [
            ('white', 'male'),
            ('white', 'female'),
            ('black', 'male'),
            ('latino', 'male'),
            ('asian', 'female'),
        ])
        self.assertColumnTypes(pivot_table, [Text, Text, Number, Number])

    def test_pivot_multiple_keys_no_pivot(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot(['race', 'gender'])

        pivot_rows = (
            ('white', 'male', 1),
            ('white', 'female', 2),
            ('black', 'male', 1),
            ('latino', 'male', 1),
            ('asian', 'female', 1),
        )

        self.assertRows(pivot_table, pivot_rows)
        self.assertColumnNames(pivot_table, ['race', 'gender', 'Count'])
        self.assertColumnTypes(pivot_table, [Text, Text, Number])

    def test_pivot_default_value(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot('race', 'gender', default_value=None)

        pivot_rows = (
            ('white', 1, 2),
            ('black', 1, None),
            ('latino', 1, None),
            ('asian', None, 1)
        )

        self.assertColumnNames(pivot_table, ['race', 'male', 'female'])
        self.assertColumnTypes(pivot_table, [Text, Number, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_compute(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot('gender', computation=Percent('Count'))

        pivot_table.print_table(output=sys.stdout)

        pivot_rows = (
            ('male', Decimal(50)),
            ('female', Decimal(50)),
        )

        self.assertColumnNames(pivot_table, ['gender', 'Percent'])
        self.assertColumnTypes(pivot_table, [Text, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_compute_pivots(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot('gender', 'color', computation=Percent('Count'))

        pivot_table.print_table(output=sys.stdout)

        pivot_rows = (
            ('male', Decimal(50), 0),
            ('female', Decimal(1) / Decimal(6) * Decimal(100), Decimal(1) / Decimal(3) * Decimal(100)),
        )

        self.assertColumnNames(pivot_table, ['gender', 'blue', 'green'])
        self.assertColumnTypes(pivot_table, [Text, Number, Number])
        self.assertRows(pivot_table, pivot_rows)

    def test_pivot_compute_kwargs(self):
        table = Table(self.rows, self.column_names, self.column_types)

        pivot_table = table.pivot('gender', 'color', computation=Percent('Count', total=8))

        pivot_table.print_table(output=sys.stdout)

        pivot_rows = (
            ('male', Decimal(3) / Decimal(8) * Decimal(100), 0),
            ('female', Decimal(1) / Decimal(8) * Decimal(100), Decimal(2) / Decimal(8) * Decimal(100)),
        )

        self.assertColumnNames(pivot_table, ['gender', 'blue', 'green'])
        self.assertColumnTypes(pivot_table, [Text, Number, Number])
        self.assertRows(pivot_table, pivot_rows)
