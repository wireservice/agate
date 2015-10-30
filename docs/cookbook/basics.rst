======
Basics
======

You could always use Python's builtin :mod:`csv` to read and write CSV files, but agate also includes custom versions that ensure correct handling of unicode characters.

Load table from a CSV
=====================

Assuming your file has a single row of headers:

.. code-block:: python

    text_type = agate.Text()
    number_type = agate.Number()

    column_names = ['city', 'area', 'population']
    column_types = [text_type, number_type, number_type]

    table = agate.Table.from_csv('population.csv', column_names, column_types)

If your file does not have headers:

.. code-block:: python

    table = agate.Table.from_csv('population.csv', column_names, column_types, header=False)

Write a table to a CSV
======================

.. code-block:: python

    table.to_csv('output.csv')

Load table from unicode CSV
===========================

You don't have to do anything special. It just works!

Load table from latin1 CSV
==========================

.. code-block:: python

    table = agate.Table.from_csv('census.csv', column_names, column_types, encoding='latin1')

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

Guess column types
==================

When loading data into a :class:`.Table` instead of specifying each column's type you can instead opt to have agate "guess" what the type of each column is. The advantage of this is that it's much quicker to get started with your analysis. The disadvantage is that it might sometimes guess wrong. Either way, using this feature will never break your code. If agate can't figure out the type of a column it was always fall back to :class:`.Text`.

The class which implements the type guessing is :class:`.TypeTester`. It supports a :code:`force` argument which allows you to override the type guessing.

.. code-block:: python

    tester = agate.TypeTester(force={
        'fips': agate.Text()
    })

    table = agate.Table.from_csv('counties.csv', column_types=tester)

.. note::

    For larger datasets the :class:`.TypeTester` can be slow to evaluate the data. You can specify a `limit` argument to reduce the number of rows that are tested, but you may also want to consider using a tool such as `proof <http://proof.readthedocs.org/en/latest/>`_ so you don't have to run it everytime you work with your data.

Reorder columns
===============

You can reorder the columns in a table by using the :meth:`.Table.select` method and specifying the column names in the order you want:

.. code-block:: python

    new_table = table.select(['3rd_column_name', '1st_column_name', '2nd_column_name'])
