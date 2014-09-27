=======
Sorting
=======

Basic sort
==========

Order a table by the :code:`last_name` column:

.. code-block:: python

    new_table = table.order_by('last_name')


Multicolumn sort
================

Because Python's internal sorting works natively with arrays, we can implement multi-column sort by returning an array from the key function.

.. code-block:: python

    new_table = table.order_by(lambda row: [row['last_name'], row['first_name'])

This table will now be ordered by :code:`last_name`, then :code:`first_name`.

Randomizing order
=================

.. code-block:: python

    import random

    new_table = table.order_by(lambda row: random.random())

