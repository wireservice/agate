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

    new_table = table.where(lambda row: not re.match('\d{3}-\d{3}-\d{4}'))

Filter by glob
--------------

TODO

Filter to values within a range
-------------------------------

TODO

Emulating Excel
===============

Formulas
--------

TODO

Pivot tables
------------

TODO

VLOOKUP
-------

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

