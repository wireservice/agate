====================
journalism |release|
====================

About
=====

.. include:: ../README

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
    nosetests

Usage
=====

Here is an example of how to use journalism, using financial aid data from data.gov:

.. code-block:: ruby

    import csv

    from journalism import Table, TextColumn, IntColumn

    COLUMNS = [
        ('state', TextColumn),
        ('state_abbr', TextColumn),
        ('9_11_gi_bill1', IntColumn),
        ('montogomery_gi_bill_active', IntColumn),
        ('montgomery_gi_bill_reserve', IntColumn),
        ('dependants', IntColumn),
        ('reserve', IntColumn),
        ('vietnam', IntColumn),
        ('total', IntColumn)
    ]

    COLUMN_NAMES = [c[0] for c in COLUMNS]
    COLUMN_TYPES = [c[1] for c in COLUMNS]

    with open('examples/realdata/Datagov_FY10_EDU_recp_by_State.csv') as f:
        # Skip headers
        f.next()
        f.next()
        f.next()

        rows = list(csv.reader(f))

    # Trim cruft off end
    rows = rows[:-2]

    table = Table(rows, COLUMN_TYPES, COLUMN_NAMES, cast=True)

    print 'Total of all states: %i' % table.columns['total'].sum()

    sort_by_total_desc = table.sort_by('total', reverse=True)

    top_five = sort_by_total_desc.rows[0:5]

    for i, row in enumerate(top_five):
        print '# %i: %s %i' % (i, row['state'], row['total'])

    last_place = sort_by_total_desc.rows[-1]

    print 'Lowest state: %(state)s %(total)i' % (last_place)

    stdev = table.columns['total'].stdev()

    print 'Standard deviation of totals: %.2f' % stdev

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

