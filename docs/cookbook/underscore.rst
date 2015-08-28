=======================
Emulating Underscore.js
=======================

filter
======

agate's :meth:`.Table.where` functions exactly like Underscore's :code:`filter`.

.. code-block:: python

    new_table = table.where(lambda row: row['state'] == 'Texas')

reject
======

To simulate Underscore's :code:`reject`, simply negate the return value of the function you pass into agate's :meth:`.Table.where`.

.. code-block:: python

    new_table = table.where(lambda row: not (row['state'] == 'Texas'))

find
====

agate's :meth:`.Table.find` works exactly like Undrescore's :code:`find`.

.. code-block:: python

    row = table.find(lambda row: row['state'].startswith('T'))

any
===

agate's columns have an :meth:`.Column.any` method that functions like Underscore's :code:`any`.

.. code-block:: python

    true_or_false = table.columns['salaries'].any(lambda d: d > 100000)

You can also use :meth:`.Table.where` to filter to columns that pass the truth test.

all
===

agate's columns have an :meth:`.Column.all` method that functions like Underscore's :code:`all`.

.. code-block:: python

    true_or_false = table.columns['salaries'].all(lambda d: d > 100000)

You can also use :meth:`.Table.where` to filter to columns that pass the truth test.
