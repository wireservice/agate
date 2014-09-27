====================
journalism |release|
====================

About
=====

.. include:: ../README

Why journalism?
===============

Why use journalism?

* A clean, readable API.
* Optimized for exploratory use in the shell.
* A full set of SQL-like operations.
* Full unicode support.
* Decimal precision everywhere.
* Pure Python. It works everywhere.
* 100% test coverage.
* Extensive user documentation.
* Access to the full power of Python in every command.

Example usage
=============

Here is an example of how to use journalism, using financial aid data from data.gov:

.. code-block:: python

    #!/usr/bin/env python

    import csv

    from journalism import Table, TextType, NumberType

    text_type = TextType()
    number_type = NumberType()

    COLUMNS = ( 
        ('state', text_type),
        ('state_abbr', text_type),
        ('9_11_gi_bill1', number_type),
        ('montogomery_gi_bill_active', number_type),
        ('montgomery_gi_bill_reserve', number_type),
        ('dependants', number_type),
        ('reserve', number_type),
        ('vietnam', number_type),
        ('total', number_type)
    )

    COLUMN_NAMES = tuple(c[0] for c in COLUMNS)
    COLUMN_TYPES = tuple(c[1] for c in COLUMNS)

    with open('examples/realdata/Datagov_FY10_EDU_recp_by_State.csv') as f:
        # Skip headers
        next(f)
        next(f)
        next(f)

        rows = list(csv.reader(f))

    # Trim cruft off end
    rows = rows[:-2]

    # Create the table
    table = Table(rows, COLUMN_TYPES, COLUMN_NAMES)

    # Remove Philippines and Puerto Rico
    states = table.where(lambda r: r['state_abbr'] not in ('PR', 'PH'))

    # Sum total of all states
    print('Total of all states: %i' % states.columns['total'].sum())

    # Sort state total, descending
    order_by_total_desc = states.order_by('total', reverse=True)

    # Grab just the top 5 states
    top_five = order_by_total_desc.rows[:5]

    for i, row in enumerate(top_five):
        print('# %i: %s %i' % (i, row['state'], row['total']))

    with open('sorted.csv', 'w') as f:
        writer = csv.writer(f)

        writer.writerow(order_by_total_desc.get_column_names())
        writer.writerows(order_by_total_desc.rows)

    # Grab just the bottom state
    last_place = order_by_total_desc.rows[-1]

    print('Lowest state: %(state)s %(total)i' % last_place)

    # Calculate the standard of deviation for the state totals
    stdev = states.columns['total'].stdev()

    print('Standard deviation of totals: %.2f' % stdev)


Table of contents
=================

.. toctree::
    :maxdepth: 3 
    
    install
    api 
    cookbook
    contributing

Authors
=======

.. include:: ../AUTHORS

License
=======

.. include:: ../COPYING

Changelog
=========

.. include:: ../CHANGELOG

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

