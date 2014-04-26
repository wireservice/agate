========
Cookbook 
========

The basics
==========

Loading a CSV
-------------

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

Loading a CSV w/ csvkit
-----------------------

TODO

Filtering
=========

Filter by regex
---------------

TODO

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
