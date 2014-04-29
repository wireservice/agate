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

    column_names = ('city', 'area', 'population')
    column_types = (TextColumn, FloatColumn, IntColumn)

    with open('population.csv') as f:
        rows = list(csv.reader(f) 

    table = Table(rows, column_types, column_names)

If your file does have headers:

.. code-block:: python

    column_types = (TextColumn, FloatColumn, IntColumn)

    with open('population.csv') as f:
        rows = list(csv.reader(f))

    column_names = rows.pop(0)

    table = Table(rows, column_types, column_names)

Loading a table from a CSV w/ csvkit
-------------------------------------

Of course, cool kids use `csvkit <http://csvkit.rtfd.org/>`_. (Hint: it supports unicode!)

.. code-block:: python

    import csvkit

    column_types = (TextColumn, FloatColumn, IntColumn)

    with open('population.csv') as f:
        rows = list(csvkit.reader(f))

    column_names = rows.pop(0)

    table = Table(rows, column_types, column_names)

Writing a table to a CSV
------------------------

.. code-block:: python

    with open('output.csv') as f:
        writer = csv.writer(f)

        writer.writerow(table.get_column_names())
        writer.writerows(table.rows)

Writing a table to a CSV w/ csvkit
----------------------------------

.. code-block:: python

    with open('output.csv') as f:
        writer = csvkit.writer(f)

        writer.writerow(table.get_column_names())
        writer.writerows(table.rows)

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

    new_table = table.where(lambda row: not re.match('\d{3}-\d{3}-\d{4}', row['phone']))

Filter by glob
--------------

Hate regexes? You can use glob (a.k.a. :mod:`fnmatch`) syntax too!

.. code-block:: python

    from fnmatch import fnmatch

    new_table = table.where(lambda row: fnmatch('C*', row['state'])

Filter to values within a range
-------------------------------

This snippet filters the dataset to incomes between 100,000 and 200,000.

.. code-block:: python

    new_table = table.where(lambda row: 100000 < row['income'] < 200000) 

Random sample
--------------

By combining a random sort with limiting, we can effectively get a random sample from a table.

.. code-block:: python

    import random

    randomized = table.order_by(lambda row: random.random())
    sampled = table.limit(10)

Ordered sample
--------------

With can also get an ordered sample by simply using the :code:`step` parameter of the :meth:`.Table.limit` method to get every Nth row.

.. code-block:: python

    sampled = table.limit(step=10)

Sorting
=======

Basic sort
----------

Order a table by the :code:`last_name` column:

.. code-block:: python

    new_table = table.order_by(lambda row: row['last_name'])


Multicolumn sort
----------------

Because Python's internal sorting works natively with arrays, we can implement multi-column sort by returning an array from the order function.

.. code-block:: python

    new_table = table.order_by(lambda row: [row['last_name'], row['first_name'])

This table will now be ordered by :code:`last_name`, then :code:`first_name`.

Randomizing order
-----------------

.. code-block:: python

    import random

    new_table = table.order_by(lambda row: random.random())

Modifying data
==============

Computing percent change
------------------------

You could use :meth:`.Table.compute` to calculate percent change, however, for your convenience journalism has a builtin shorthand:

.. code-block:: python

    new_table = table.percent_change('july', 'august', 'pct_change')

This will compute the percent change between the :code:`july` and :code:`august` columns and put the result in a new :code:`pct_change` column in the resulting table.

Rounding to two decimal places
------------------------------

journalism stores fractional values using Python's :class:`decimal.Decimal` type. This data type ensures numerical precision beyond what is supported by the native :func:`float` type, however, because of this we can not use Python's builtin :func:`round` function. Instead we must use :meth:`decimal.Decimal.quantize`.

We can use :meth:`.Table.compute` to apply the quantize to generate a rounded column from an existing one:

.. code-block:: python

    from decimal import Decimal

    def round_price(row):
        return row['price'].quantize(Decimal('0.01'))

    new_table = table.compute('price_rounded', DecimalColumn, round_price)

To round to one decimal place you would simply change :code:`0.01` to :code:`0.1`.

Emulating SQL
=============

journalism's command structure is very similar to SQL. The primary difference between journalism and SQL is that commands like :code:`SELECT` and :code:`WHERE` explicitly create new tables. You can chain them together as you would with SQL, but be aware each command is actually creating a new table.

SELECT
------

SQL:

.. code-block:: sql

    SELECT state, total FROM table;

journalism:

.. code-block:: python

    new_table = table.select(('state', 'total'))

WHERE
-----

SQL:

.. code-block:: sql

    SELECT * FROM table WHERE LOWER(state) = 'california';

journalism:

.. code-block:: python

    new_table = table.where(lambda row: row['state'].lower() == 'california')

ORDER BY
--------

SQL:

.. code-block:: sql

    SELECT * FROM table ORDER BY total DESC;

journalism:

.. code-block:: python

    new_table = table.where(lambda row: row['total'], reverse=True)

Chaining commands together
--------------------------

SQL:

.. code-block:: SQL

    SELECT state, total FROM table WHERE LOWER(state) = 'california' ORDER BY total DESC;

journalism:

.. code-block:: python

    new_table = table \
        .select(('state', 'total')) \
        .where(lambda row: row['state'].lower() == 'california') \
        .order_by(lambda row: row['total'], reverse=True)

.. note::

    I don't advise chaining commands like this. Being explicit about each step is usually better.

DISTINCT
--------

SQL:

.. code-block:: sql

    SELECT DISTINCT ON (state) * FROM table;

journalism:

.. code-block:: python

    new_table = table.distinct(lamda row: row['state'])

.. note::

    Unlike most SQL implementations, journalism always returns the full row. Use :meth:`.Table.select` if you want to filter the columns first.

INNER JOIN
----------

TODO

LEFT OUTER JOIN
---------------

TODO


GROUP BY
--------

TODO

Emulating Excel
===============

One of journalism's most powerful assets is that instead of a wimpy "formula" language, you have the entire Python language at your disposal. Here are examples of how to translate a few common Excel operations.

SUM
---

.. code-block:: python

    def five_year_total(row):
        columns = ('2009', '2010', '2011', '2012', '2013')

        return sum(tuple(row[c] for c in columns)]

    new_table = table.compute('five_year_total', DecimalColumn, five_year_total)  

TRIM
----

.. code-block:: python

    new_table = table.compute('name_stripped', TextColumn, lambda row: row['name'].strip())

CONCATENATE
-----------

.. code-block:: python

    new_table = table.compute('full_name', TextColumn, lambda row '%(first_name)s %(middle_name)s %(last_name)s' % row) 

IF
--

.. code-block:: python

    new_table = table.compute('mvp_candidate', TextColumn, lambda row: 'Yes' if row['batting_average'] > 0.3 else 'No'

VLOOKUP
-------

.. code-block:: python

    states = {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        ...
    }

    new_table = table.compute('state_name', TextColumn, lambda row: states[row['state_abbr']]) 

Pivot tables
------------

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

Plotting with matplotlib
========================

journalism integrates well with Python plotting library `matplotlib <http://matplotlib.org/>`_.

Line chart
----------

.. code-block:: python

    import pylab

    pylab.plot(table.columns['homeruns'], table.columns['wins'])
    pylab.xlabel('Homeruns')
    pylab.ylabel('Wins')
    pylab.title('How homeruns correlate to wins')

    pylab.show()

Histogram
---------

.. code-block:: python

    pylab.hist(table.columns['state'])

    pylab.xlabel('State')
    pylab.ylabel('Count')
    pylab.title('Count by state')

    pylab.show()

Plotting with pygal
===================

`pygal <http://pygal.org/>`_ is a neat library for generating SVG charts. journalism works well with it too.

Line chart
----------

.. code-block:: python

    import pygal

    line_chart = pygal.Line()
    line_chart.title = 'State totals'
    line_chart.x_labels = states.columns['state_abbr']
    line_chart.add('Total', states.columns['total'])
    line_chart.render_to_file('total_by_state.svg') 


