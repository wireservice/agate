==================
Compute new values
==================

Change
======

.. code-block:: python

    new_table = table.compute([
        ('2000_change', agate.Change('2000', '2001')),
        ('2001_change', agate.Change('2001', '2002')),
        ('2002_change', agate.Change('2002', '2003'))
    ])

Or, better yet, compute the whole decade using a loop:

.. code-block:: Python

    computations = []

    for year in range(2000, 2010):
        change = agate.Change(year, year + 1)
        computations.append(('%i_change' % year, change))

    new_table = table.compute(computations)

Percent
=======

Calculate the percentage for each value in a column with :class:`.Percent`.
Values are divided into the sum of the column by default.

.. code-block:: python

    columns = ('value',)
    rows = ([1],[2],[2],[5])
    new_table = agate.Table(rows, columns)

    new_table = new_table.compute([
        ('percent', agate.Percent('value'))
    ])

    new_table.print_table()

    | value | percent |
    | ----- | ------- |
    |     1 |      10 |
    |     2 |      20 |
    |     2 |      20 |
    |     5 |      50 |

Override the denominator with a keyword argument.

.. code-block:: python

    new_table = new_table.compute([
        ('percent', agate.Percent('value', 5))
    ])

    new_table.print_table()

    | value | percent |
    | ----- | ------- |
    |     1 |      20 |
    |     2 |      40 |
    |     2 |      40 |
    |     5 |     100 |

Percent change
==============

Want percent change instead of value change? Just swap out the :class:`.Computation`:

.. code-block:: Python

    computations = []

    for year in range(2000, 2010):
        change = agate.PercentChange(year, year + 1)
        computations.append(('%i_change' % year, change))

    new_table = table.compute(computations)

Indexed/cumulative change
=========================

Need your change indexed to a starting year? Just fix the first argument:

.. code-block:: Python

    computations = []

    for year in range(2000, 2010):
        change = agate.Change(2000, year + 1)
        computations.append(('%i_change' % year, change))

    new_table = table.compute(computations)

Of course you can also use :class:`.PercentChange` if you need percents rather than values.

Round to two decimal places
===========================

agate stores numerical values using Python's :class:`decimal.Decimal` type. This data type ensures numerical precision beyond what is supported by the native :func:`float` type, however, because of this we can not use Python's builtin :func:`round` function. Instead we must use :meth:`decimal.Decimal.quantize`.

We can use :meth:`.Table.compute` to apply the quantize to generate a rounded column from an existing one:

.. code-block:: python

    from decimal import Decimal

    number_type = agate.Number()

    def round_price(row):
        return row['price'].quantize(Decimal('0.01'))

    new_table = table.compute([
        ('price_rounded', agate.Formula(number_type, round_price))
    ])

To round to one decimal place you would simply change :code:`0.01` to :code:`0.1`.

.. _difference_between_dates:

Difference between dates
========================

Calculating the difference between dates (or dates and times) works exactly the same as it does for numbers:

.. code-block:: python

    new_table = table.compute([
        ('age_at_death', agate.Change('born', 'died'))
    ])

Levenshtein edit distance
=========================

The Levenshtein edit distance is a common measure of string similarity. It can be used, for instance, to check for typos between manually-entered names and a version that is known to be spelled correctly.

Implementing Levenshtein requires writing a custom :class:`.Computation`. To save ourselves building the whole thing from scratch, we will lean on the `python-Levenshtein <https://pypi.python.org/pypi/python-Levenshtein/>`_ library for the actual algorithm.

.. code-block:: python

    import agate
    from Levenshtein import distance
    
    class LevenshteinDistance(agate.Computation):
        """
        Computes Levenshtein edit distance between the column and a given string.
        """
        def __init__(self, column_name, compare_string):
            self._column_name = column_name
            self._compare_string = compare_string

        def get_computed_data_type(self, table):
            """
            The return value is a numerical distance.
            """
            return agate.Number()

        def validate(self, table):
            """
            Verify the column is text.
            """
            column = table.columns[self._column_name]

            if not isinstance(column.data_type, agate.Text):
                raise agate.DataTypeError('Can only be applied to Text data.')

        def run(self, table):
            """
            Find the distance, returning null when the input column was null.
            """
            new_column = []

            for row in table.rows:
              val = row[self._column_name]

              if val is None:
                  new_column.append(None)
              else:
                  new_column.append(distance(val, self._compare_string))

            return new_column

This code can now be applied to any :class:`.Table` just as any other :class:`.Computation` would be:

.. code-block:: python

    new_table = table.compute([
        ('distance', LevenshteinDistance('column_name', 'string to compare'))
    ])

The resulting column will contain an integer measuring the edit distance between the value in the column and the comparison string.

USA Today Diversity Index
=========================

The `USA Today Diversity Index <https://www.usatoday.com/story/news/nation/2014/10/21/diversity-index-data-how-we-did-report/17432103/>`_ is a widely cited method for evaluating the racial diversity of a given area. Using a custom :class:`.Computation` makes it simple to calculate.

Assuming that your data has a column for the total population, another for the population of each race and a final column for the hispanic population, you can implement the diversity index like this:

.. code-block:: python

    class USATodayDiversityIndex(agate.Computation):
        def get_computed_data_type(self, table):
            return agate.Number()

        def run(self, table):
            new_column = []

            for row in table.rows:
              race_squares = 0

              for race in ['white', 'black', 'asian', 'american_indian', 'pacific_islander']:
                  race_squares += (row[race] / row['population']) ** 2

              hispanic_squares = (row['hispanic'] / row['population']) ** 2
              hispanic_squares += (1 - (row['hispanic'] / row['population'])) ** 2

              new_column.append((1 - (race_squares * hispanic_squares)) * 100)

            return new_column

We apply the diversity index like any other computation:

.. code-block:: Python

    with_index = table.compute([
        ('diversity_index', USATodayDiversityIndex())
    ])

Simple Moving Average
=====================

A simple moving average is the average of some number of prior values in a series. It is typically used to smooth out variation in time series data.

The following custom :class:`.Computation` will compute a simple moving average. This example assumes your data is already sorted.

.. code-block:: python

    class SimpleMovingAverage(agate.Computation):
        """
        Computes the simple moving average of a column over some interval.
        """
        def __init__(self, column_name, interval):
            self._column_name = column_name
            self._interval = interval

        def get_computed_data_type(self, table):
            """
            The return value is a numerical average.
            """
            return agate.Number()

        def validate(self, table):
            """
            Verify the column is numerical.
            """
            column = table.columns[self._column_name]

            if not isinstance(column.data_type, agate.Number):
                raise agate.DataTypeError('Can only be applied to Number data.')

        def run(self, table):
            new_column = []

            for i, row in enumerate(table.rows):
                if i < self._interval:
                    new_column.append(None)
                else:
                    values = tuple(r[self._column_name] for r in table.rows[i - self._interval:i])

                    if None in values:
                        new_column.append(None)
                    else:
                        new_column.append(sum(values) / self._interval)

            return new_column

You would use the simple moving average like so:

.. code-block:: Python

    with_average = table.compute([
        ('six_month_moving_average', SimpleMovingAverage('price', 6))
    ])
