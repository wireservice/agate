=======================
Performing calculations
=======================

Computing annual change
========================

You could use a :class:`.Formula` to calculate percent change, however, for your convenience journalism has a built-in shortcut. For example, if your spreadsheet has a column with values for each year you could do:

.. code-block:: python

    new_table = table.compute([
        ('2000_change', Change('2000', '2001'),
        ('2001_change', Change('2001', '2002'),
        ('2002_change', Change('2002', '2003')
    ])

Or, better yet, compute the whole decade using a loop:

.. code-block:: Python

    computations = []

    for year in range(2000, 2010):
        change = Change(year, year + 1)
        computations.append(('%i_change' % year, change))

    new_table = table.compute(computations)

Computing annual percent change
===============================

Want percent change instead of value change? Just swap out the :class:`.Aggregation`:

.. code-block:: Python

    computations = []

    for year in range(2000, 2010):
        change = PercentChange(year, year + 1)
        computations.append(('%i_change' % year, change))

    new_table = table.compute(computations)

Computing indexed change
========================

Need your change indexed to a starting year? Just fix the first argument:

.. code-block:: Python

    computations = []

    for year in range(2000, 2010):
        change = Change(2000, year + 1)
        computations.append(('%i_change' % year, change))

    new_table = table.compute(computations)

Of course you can also use :class:`.PercentChange` if you need percents rather than values.

Rounding to two decimal places
==============================

journalism stores numerical values using Python's :class:`decimal.Decimal` type. This data type ensures numerical precision beyond what is supported by the native :func:`float` type, however, because of this we can not use Python's builtin :func:`round` function. Instead we must use :meth:`decimal.Decimal.quantize`.

We can use :meth:`.Table.compute` to apply the quantize to generate a rounded column from an existing one:

.. code-block:: python

    from decimal import Decimal
    from journalism import NumberType

    number_type = NumberType()

    def round_price(row):
        return row['price'].quantize(Decimal('0.01'))

    new_table = table.compute([
        ('price_rounded', Formula(number_type, round_price))
    ])

To round to one decimal place you would simply change :code:`0.01` to :code:`0.1`.
