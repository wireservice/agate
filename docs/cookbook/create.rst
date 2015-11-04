===============
Creating tables
===============

You could always use Python's builtin :mod:`csv` to read and write CSV files, but agate also includes custom versions that ensure correct handling of unicode characters.

Create a table
==============

To create a table from data you have in memory:

.. code-block:: python

    column_names = ['letter', 'number']
    column_types = [agate.Text(), agate.Number()]

    rows = [
        ('a', 1),
        ('b', 2),
        ('c', None)
    ]

    table = agate.Table(rows, column_names, column_types)

Load table from a CSV
=====================

By default, loading a table from a CSV will use agate's builtin :class:`.TypeTester` to infer column types:

.. code-block::

    table = agate.Table.from_csv('filename.csv')

Override type inference
=======================

In some cases agate's :class:`.TypeTester` may guess incorrectly. To override the type for a column construct a TypeTester manually and use the `force` argument:

.. code-block::

    tester = agate.TypeTester(force={
        'column_name': agate.Text()
    })

    table = agate.Table.from_csv('filename.csv', column_types=tester)

Limit type inference
====================

For large datasets :class:`.TypeTester` may be unreasonably slow. In order to limit the amount of data it uses you can specify the `limit` argument. Note that if data after the limit invalidates the TypeTester's inference you may get errors when the data is loaded.

.. code-block::

    tester = agate.TypeTester(limit=100)

    table = agate.Table.from_csv('filename.csv', column_types=tester)

Manually specify columns
========================

If you know the types of your data you may find it more efficient to manually specify the names and types of your columns. This also gives you an opportunity to rename columns when you load them.

.. code-block:: python

    text_type = agate.Text()
    number_type = agate.Number()

    column_names = ['city', 'area', 'population']
    column_types = [text_type, number_type, number_type]

    table = agate.Table.from_csv('population.csv', column_names, column_types)

Or, you can use this method to load data from a file that does not have a header row:

.. code-block:: python

    table = agate.Table.from_csv('population.csv', column_names, column_types, header=False)

Write a table to a CSV
======================

.. code-block:: python

    table.to_csv('filename.csv')

Load table from unicode CSV
===========================

You don't have to do anything special. It just works!

Load table from latin1 CSV
==========================

.. code-block:: python

    table = agate.Table.from_csv('census.csv', encoding='latin1')

.. _load_a_table_from_a_sql_database:

Load a table from a SQL database
================================

Use the `agate-sql <http://agate-sql.readthedocs.org/>`_ extension.

.. code-block:: python

    import agatesql

    table = agate.Table.from_sql('postgresql:///database', 'input_table')

Write a table to a SQL database
===============================

Use the `agate-sql <http://agate-sql.readthedocs.org/>`_ extension.

.. code-block:: python

    import agatesql

    table.to_sql('postgresql:///database', 'output_table')
