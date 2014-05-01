====================
journalism |release|
====================

About
=====

.. include:: ../README

Features
========

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

Principles
==========

journalism is a intended to fill a very particular programming niche, that of non-professional data analysts who need to get shit done quickly. These are the principles of its development: 

* Humans have less time than computers. Always optimize for humans.
* Most datasets are simple and small. Never optimize for quants.
* Text is data. It must be a first-class citizen.
* Python gets it right. Make it work like Python does. 
* Humans are busy, stupid, lazy, etc. It must be easy.
* Mutability is confusion. Processes that alter data must create new copies.

But why not...

* numpy: It's hard.
* pandas: It's hard.
* R: Don't even get me started.
* SAS: You have that kind of money?
* SQL: It's not code.
* An ORM: Have you actually tried this?

I'm not reinventing the wheel, I'm just putting on the right size tires.

Installation
============

Users
-----

If you only want to use journalism, install it this way::

    pip install journalism 

Developers
----------

If you are a developer that also wants to hack on journalism, install it this way::

    git clone git://github.com/onyxfish/journalism.git
    cd journalism
    mkvirtualenv --no-site-packages journalism
    pip install -r requirements.txt
    python setup.py develop
    nosetests --with-coverage --cover-package=journalism

Supported platforms
-------------------

journalism supports the following versions of Python:

* Python 2.6+
* Python 3.2+
* Latest `PyPy <http://pypy.org/>`_

It is tested on OSX, but due to it's minimal dependencies should work fine on both Linux and Windows.

Usage
=====

Here is an example of how to use journalism, using financial aid data from data.gov:

.. code-block:: python

    #!/usr/bin/env python

    import csv

    from journalism import Table, TextColumn, IntColumn

    COLUMNS = ( 
        ('state', TextColumn),
        ('state_abbr', TextColumn),
        ('9_11_gi_bill1', IntColumn),
        ('montogomery_gi_bill_active', IntColumn),
        ('montgomery_gi_bill_reserve', IntColumn),
        ('dependants', IntColumn),
        ('reserve', IntColumn),
        ('vietnam', IntColumn),
        ('total', IntColumn)
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
    table = Table(rows, COLUMN_TYPES, COLUMN_NAMES, cast=True)

    # Remove Phillipines and Puerto Rico
    states = table.where(lambda r: r['state_abbr'] not in ('PR', 'PH'))

    # Sum total of all states
    print('Total of all states: %i' % states.columns['total'].sum())

    # Sort state total, descending
    order_by_total_desc = states.order_by(lambda r: r['total'], reverse=True)

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

    print('Standard deviation of totals: %.2f' % stdev)    print 'Standard deviation of totals: %.2f' % stdev

Cookbook
========

Need some more specific examples? Try these out:

.. toctree::
    :maxdepth: 3 

    cookbook

API
===

.. toctree::
    :maxdepth: 2

    api/columns
    api/exceptions
    api/rows
    api/table

Contributing
============

Want to hack on journalism? Here's how:

.. toctree::
    :maxdepth: 2

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

