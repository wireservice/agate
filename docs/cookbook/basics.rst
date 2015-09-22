======
Basics
======

You can always use Python's builtin :mod:`csv` to read and write CSV files, but agate also includes shortcuts to save time.

.. note::

    If you have `csvkit <http://csvkit.rtfd.org/>`_ installed, agate will use it instead of Python's builtin :mod:`csv`. The builting module is not unicode-safe for Python 2, so it is strongly suggested that you do install csvkit.

Load table from a CSV
=====================

Assuming your file has a single row of headers:

.. code-block:: python

    text_type = agate.Text()
    number_type = agate.Number()

    columns = (
        ('city', text_type),
        ('area', number_type),
        ('population', number_type)
    )

    table = agate.Table.from_csv('population.csv', columns)

If your file does not have headers:

.. code-block:: python

    table = agate.Table.from_csv('population.csv', columns, header=False)

Write a table to a CSV
======================

.. code-block:: python

    table.to_csv('output.csv')

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

    table = agate.Table.from_csv('counties.csv', tester)

.. note::

    For larger datasets the :class:`.TypeTester` can be slow to evaluate the data. It's best to use it with a tool such as `proof <http://proof.readthedocs.org/en/latest/>`_ so you don't have to run it everytime you work with your data.

Reorder columns
===============

You can reorder the columns in a table by using the :meth:`.Table.select` method and specifying the column names in the order you want:

.. code-block:: python

    new_table = table.select(['3rd_column_name', '1st_column_name', '2nd_column_name'])
