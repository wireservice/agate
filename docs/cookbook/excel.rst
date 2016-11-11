=============
Emulate Excel
=============

One of agate's most powerful assets is that instead of a wimpy "formula" language, you have the entire Python language at your disposal. Here are examples of how to translate a few common Excel operations.

Simple formulas
===============

If you need to simulate a simple Excel formula you can use the :class:`.Formula` class to apply an arbitrary function.

Excel:

.. code::

    =($A1 + $B1) / $C1

agate:

.. code-block:: python

    def f(row):
        return (row['a'] + row['b']) / row['c']

    new_table = table.compute([
        ('new_column', agate.Formula(agate.Number(), f))
    ])

If this still isn't enough flexibility, you can also create your own subclass of :class:`.Computation`.

SUM
===

.. code-block:: python

    number_type = agate.Number()

    def five_year_total(row):
        columns = ('2009', '2010', '2011', '2012', '2013')

        return sum(tuple(row[c] for c in columns)]

    formula = agate.Formula(number_type, five_year_total)

    new_table = table.compute([
        ('five_year_total', formula)
    ])

TRIM
====

.. code-block:: python

    new_table = table.compute([
        ('name_stripped', agate.Formula(text_type, lambda r: r['name'].strip()))
    ])

CONCATENATE
===========

.. code-block:: python

    new_table = table.compute([
        ('full_name', agate.Formula(text_type, lambda r: '%(first_name)s %(middle_name)s %(last_name)s' % r))
    ])

IF
==

.. code-block:: python

    new_table = table.compute([
        ('mvp_candidate', agate.Formula(boolean_type, lambda r: row['batting_average'] > 0.3))
    ])


VLOOKUP
=======

There are two ways to get the equivalent of Excel's VLOOKUP with agate. If your lookup source is another agate :class:`.Table`, then you'll want to use the :meth:`.Table.join` method:

.. code-block:: python

    new_table = mvp_table.join(states, 'state_abbr')

This will add all the columns from the `states` table to the `mvp_table`, where their `state_abbr` columns match.

If your lookup source is a Python dictionary or some other object you can implement the lookup using a :class:`.Formula` computation:

.. code-block:: python

    states = {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        ...
    }

    new_table = table.compute([
        ('mvp_candidate', agate.Formula(text_type, lambda r: states[row['state_abbr']]))
    ])

Pivot tables as cross-tabulations
=================================

Pivot tables in Excel implement a tremendous range of functionality. Agate divides this functionality into a few different methods.

If what you want is to convert rows to columns to create a "crosstab", then you'll want to use the :meth:`.Table.pivot` method:

.. code-block:: python

    jobs_by_state_and_year = employees.pivot('state', 'year')

This will generate a table with a row for each value in the `state` column and a column for each value in the `year` column. The intersecting cells will contains the counts grouped by state and year. You can pass the `aggregation` keyword to aggregate some other value, such as :class:`.Mean` or :class:`.Median`.

Pivot tables as summaries
=========================

On the other hand, if what you want is to summarize your table with descriptive statistics, then you'll want to use :meth:`.Table.group_by` and :meth:`.TableSet.aggregate`:

.. code-block:: python

    jobs = employees.group_by('job_title')
    summary = jobs.aggregate([
        ('employee_count', agate.Count()),
        ('salary_mean', agate.Mean('salary')),
        ('salary_median', agate.Median('salary'))
    ])

The resulting ``summary`` table will have four columns: ``job_title``, ``employee_count``, ``salary_mean`` and ``salary_median``.

You may also want to look at the :meth:`.Table.normalize` and :meth:`.Table.denormalize` methods for examples of functionality frequently accomplished with Excel's pivot tables.
