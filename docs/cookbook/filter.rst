===========
Filter rows
===========

By regex
========

You can use Python's builtin :mod:`re` module to introduce a regular expression into a :meth:`.Table.where` query.

For example, here we find all states that start with "C".

.. code-block:: python

    import re

    new_table = table.where(lambda row: re.match('^C', str(row['state'])))

This can also be useful for finding values that **don't** match your expectations. For example, finding all values in the "phone number" column that don't look like phone numbers:

.. code-block:: python

    new_table = table.where(lambda row: not re.match('\d{3}-\d{3}-\d{4}', str(row['phone'])))

By glob
=======

Hate regexes? You can use glob (:mod:`fnmatch`) syntax too!

.. code-block:: python

    from fnmatch import fnmatch

    new_table = table.where(lambda row: fnmatch('C*', row['state']))

Values within a range
=====================

This snippet filters the dataset to incomes between 100,000 and 200,000.

.. code-block:: python

    new_table = table.where(lambda row: 100000 < row['income'] < 200000)

Dates within a range
====================

This snippet filters the dataset to events during the summer of 2015:

.. code-block:: python

    import datetime

    new_table = table.where(lambda row: datetime.datetime(2015, 6, 1) <= row['date'] <= datetime.datetime(2015, 8, 31))

If you want to filter to events during the summer of any year:

.. code-block:: python

    new_table = table.where(lambda row: 6 <= row['date'].month <= 8)

Top N percent
=============

To filter a dataset to the top 10% percent of values we first compute the percentiles for the column and then use the result in the :meth:`.Table.where` truth test:

.. code-block:: python

    percentiles = table.aggregate(agate.Percentiles('salary'))
    top_ten_percent = table.where(lambda r: r['salary'] >= percentiles[90])

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

Distinct values
===============

You can retrieve a distinct list of values in a column using :meth:`.Column.values_distinct` or :meth:`.Table.distinct`.

:meth:`.Table.distinct` returns the entire row so it's necessary to chain a select on the specific column.

.. code-block:: python

    columns = ('value',)
    rows = ([1],[2],[2],[5])
    new_table = agate.Table(rows, columns)

    new_table.columns['value'].values_distinct()
    # or
    new_table.distinct('value').columns['value'].values()
    (Decimal('1'), Decimal('2'), Decimal('5'))
