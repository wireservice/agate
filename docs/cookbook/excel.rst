===============
Emulating Excel
===============

One of journalism's most powerful assets is that instead of a wimpy "formula" language, you have the entire Python language at your disposal. Here are examples of how to translate a few common Excel operations.

Simple formulas
===============

If you need to simulate a simple Excel formula you can use the :class:`.Formula` class to apply an arbitrary function.

Excel:

.. code::

    =($A1 + $B1) / $C1

journalism:

.. code-block:: python

    def f(row):
        return (row['a'] + row['b']) / row['c']

    new_table = table.compute([
        ('new_column', Formula(f))
    ])

If this still isn't enough flexibility, you can also create your own subclass of :class:`.Computation`.

SUM
===

.. code-block:: python

    from journalism import NumberType, Formula

    number_type = NumberType()

    def five_year_total(row):
        columns = ('2009', '2010', '2011', '2012', '2013')

        return sum(tuple(row[c] for c in columns)]

    formula = Formula(number_type, five_year_total)

    new_table = table.compute([
        ('five_year_total', formula)
    ])

TRIM
====

.. code-block:: python

    new_table = table.compute([
        ('name_stripped', Formula(text_type, lambda r: r['name'].strip()))
    ])

CONCATENATE
===========

.. code-block:: python

    new_table = table.compute([
        ('full_name', Formula(text_type, lambda r: '%(first_name)s %(middle_name)s %(last_name)s' % r))
    ])

IF
==

.. code-block:: python

    new_table = table.compute([
        ('mvp_candidate', Formula(boolean_type, lambda r: row['batting_average'] > 0.3))
    ])


VLOOKUP
=======

.. code-block:: python

    states = {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        ...
    }

    new_table = table.compute([
        ('mvp_candidate', Formula(text_type, lambda r: states[row['state_abbr']]))
    ])

Pivot tables
============

You can emulate most of the functionality of Excel's pivot tables using the :meth:`.TableSet.aggregate` method.

.. code-block:: python

    professions = data.group_by('profession')
    summary = professions.aggregate([
        ('salary', 'mean'),
        ('salary', 'median')
    ])

The resulting ``summary`` table will have four columns: ``group`` (the profession), ``count`` (the number of grouped rows), ``salary_mean`` and ``salary_median`` (the aggregates).
