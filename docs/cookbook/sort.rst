====
Sort
====

Alphabetical
============

Order a table by the :code:`last_name` column:

.. code-block:: python

    new_table = table.order_by('last_name')

Numerical
=========

Order a table by the :code:`cost` column:

.. code-block:: python

    new_table = table.order_by('cost')

.. _sort_by_date:

By date
=======

Order a table by the :code:`birth_date` column:

.. code-block:: python

    new_table = table.order_by('birth_date')

Reverse order
=============

The order of any sort can be reversed by using the :code:`reverse` keyword:

.. code-block:: python

    new_table = table.order_by('birth_date', reverse=True)

Multiple columns
================

Because Python's internal sorting works natively with sequences, we can implement multi-column sort by returning a tuple from the key function.

.. code-block:: python

    new_table = table.order_by(lambda row: (row['last_name'], row['first_name']))

This table will now be ordered by :code:`last_name`, then :code:`first_name`.

Random order
============

.. code-block:: python

    import random

    new_table = table.order_by(lambda row: random.random())
