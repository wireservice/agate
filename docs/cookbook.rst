========
Cookbook 
========

The basics
==========

Loading a table from a CSV
--------------------------

You can use Python's builtin :mod:`csv` to read CSV files.

If your file does not have headers:

.. code-block:: python

    from journalism import Table, TextColumn, IntColumn, FloatColumn

    column_names = ['city', 'area', 'population']
    column_types = [TextColumn, FloatColumn, IntColumn]

    with open('population.csv') as f:
        rows = list(csv.reader(f) 

    table = Table(rows, column_types, column_names)

If your file does have headers:

.. code-block:: python

    column_types = [TextColumn, FloatColumn, IntColumn]

    with open('population.csv') as f:
        rows = list(csv.reader(f))

    # Omitting third argument will cause journalism to use
    # first row as column names
    table = Table(rows, column_types)

Loading a table from a CSV w/ csvkit
-------------------------------------

TODO

Writing data to a CSV
---------------------

.. code-block:: python

    with open('output.csv') as f:
        writer = csv.writer(f)

        writer.writerow(table.get_column_names())
        writer.writerows(table.get_data())

Writing data to a CSV w/ csvkit
-------------------------------

TODO

Filtering
=========

Filter by regex
---------------

You can use Python's builtin :mod:`re` module to introduce a regular expression into a :meth:`.Table.where` query.

For example, here we find all states that start with "C".

.. code-block:: python

    import re

    new_table = table.where(lambda row: re.match('^C', row['state']))

This can also be useful for finding values that **don't** match your expectations. For example, finding all values in the "phone number" column that don't look like phone numbers:

.. code-block:: python

    new_table = table.where(lambda row: not re.match('\d{3}-\d{3}-\d{4}', row['phone']))

Filter by glob
--------------

TODO

Filter to values within a range
-------------------------------

TODO

Modifying data
==============

Rounding to two decimal places
------------------------------

journalism stores fractional values using Python's :class:`decimal.Decimal` type. This data type ensures numerical precision beyond what is supported by the native :func:`float` type, however, because of this we can not use Python's builtin :func:`round` function. Instead we must use :meth:`decimal.Decimal.quantize`.

We can use :meth:`.Table.compute` to apply the quantize to generate a rounded column from an existing one:

.. code-block:: python

    from decimal import Decimal

    def round_price(row):
        return row['price'].quantize(Decimal('0.01'))

    new_table = table.compute('price_rounded', DecimalColumn, round_price)

To round to one decimal place you would simply change :code:`0.01` to :code:`0.1`.

Emulating Excel
===============

One of journalism's most powerful assets is that instead of a wimpy "formula" language, you have the entire Python language at your disposal. Here are examples of how to translate a few common Excel operations.

SUM
---

.. code-block:: python

    def five_year_total(row):
        columns = ['2009', '2010', '2011', '2012', '2013']

        return sum([row[c] for c in columns]]

    new_table = table.compute('five_year_total', DecimalColumn, five_year_total)  

TRIM
----

.. code-block:: python

    new_table = table.compute('name_stripped', TextColumn, lambda row: row['name'].strip())

CONCATENATE
-----------

.. code-block:: python

    new_table = table.compute('full_name', TextColumn, lambda row '%(first_name)s %(middle_name)s %(last_name)s' % row) 

IF
--

.. code-block:: python

    new_table = table.compute('mvp_candidate', TextColumn, lambda row: 'Yes' if row['batting_average'] > 0.3 else 'No'

VLOOKUP
-------

TODO

Pivot tables
------------

TODO

Emulating Underscore.js
=======================

filter
------

journalism's :meth:`.Table.where` functions exactly like Underscore's `filter`.

.. code-block:: python

    new_table = table.where(lambda row: row['state'] == 'Texas')

reject
------

To simulate Underscore's `reject`, simply negate the return value of the function you pass into journalism's :meth:`.Table.where`.

.. code-block:: python

    new__table = table.where(lambda row: not (row['state'] == 'Texas'))

