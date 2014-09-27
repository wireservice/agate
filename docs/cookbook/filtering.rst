=========
Filtering
=========

Filter by regex
===============

You can use Python's builtin :mod:`re` module to introduce a regular expression into a :meth:`.Table.where` query.

For example, here we find all states that start with "C".

.. code-block:: python

    import re

    new_table = table.where(lambda row: re.match('^C', row['state']))

This can also be useful for finding values that **don't** match your expectations. For example, finding all values in the "phone number" column that don't look like phone numbers:

.. code-block:: python

    new_table = table.where(lambda row: not re.match('\d{3}-\d{3}-\d{4}', row['phone']))

Filter by glob
==============

Hate regexes? You can use glob (a.k.a. :mod:`fnmatch`) syntax too!

.. code-block:: python

    from fnmatch import fnmatch

    new_table = table.where(lambda row: fnmatch('C*', row['state'])

Filter to values within a range
===============================

This snippet filters the dataset to incomes between 100,000 and 200,000.

.. code-block:: python

    new_table = table.where(lambda row: 100000 < row['income'] < 200000) 

Random sample
=============

By combining a random sort with limiting, we can effectively get a random sample from a table.

.. code-block:: python

    import random

    randomized = table.order_by(lambda row: random.random())
    sampled = table.limit(10)

Ordered sample
==============

With can also get an ordered sample by simply using the :code:`step` parameter of the :meth:`.Table.limit` method to get every Nth row.

.. code-block:: python

    sampled = table.limit(step=10)


