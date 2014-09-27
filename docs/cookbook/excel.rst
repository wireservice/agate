===============
Emulating Excel
===============

One of journalism's most powerful assets is that instead of a wimpy "formula" language, you have the entire Python language at your disposal. Here are examples of how to translate a few common Excel operations.

SUM
===

.. code-block:: python

    def five_year_total(row):
        columns = ('2009', '2010', '2011', '2012', '2013')

        return sum(tuple(row[c] for c in columns)]

    new_table = table.compute('five_year_total', DecimalColumn, five_year_total)  

TRIM
====

.. code-block:: python

    new_table = table.compute('name_stripped', TextType(), lambda row: row['name'].strip())

CONCATENATE
===========

.. code-block:: python

    new_table = table.compute('full_name', TextType(), lambda row '%(first_name)s %(middle_name)s %(last_name)s' % row) 

IF
==

.. code-block:: python

    new_table = table.compute('mvp_candidate', TextType(), lambda row: 'Yes' if row['batting_average'] > 0.3 else 'No'

VLOOKUP
=======

.. code-block:: python

    states = {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        ...
    }

    new_table = table.compute('state_name', TextType(), lambda row: states[row['state_abbr']]) 

Pivot tables
============

You can emulate most of the functionality of Excel's pivot tables using the :meth:`.Table.aggregate` method.

.. code-block:: python

    summary = table.aggregate('profession', (('salary', 'mean'), ('salary', 'median')) 

A "count" column is always return in the results. The :code:`summary` table in this example would have these columns: :code:`('profession', 'profession_count', 'salary_mean', 'salary_median')`.

