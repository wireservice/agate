===============
agate |release|
===============

About
=====

.. include:: ../README

Why agate?
==========

* A readable and user-friendly API.
* A robust set of SQL-like operations.
* Unicode support everywhere.
* Decimal precision everywhere.
* Exhaustive user documentation.
* Pluggable extensions to add `SQL integration <http://agate-sql.readthedocs.org/>`_, `statistical methods <http://agate-stats.readthedocs.org/>`_, etc.
* Designed with `iPython <http://ipython.org/>`_, `Jupyter <https://jupyter.org/>`_ and `atom/hydrogen <https://atom.io/packages/hydrogen>`_ in mind.
* Pure Python. No huge C dependencies to compile.
* 100% test coverage.
* MIT licensed. Free for all purposes.
* Zealously `zen <https://www.python.org/dev/peps/pep-0020/>`_.

Show me code
============

.. code-block:: python

    import agate

    purchases = agate.Table.from_csv('examples/realdata/ks_1033_data.csv')

    by_county = purchases.group_by('county')

    totals = by_county.aggregate([
        ('total_cost', agate.Sum(), 'county_cost')
    ])

    totals = totals.order_by('county_cost', reverse=True)
    totals.limit(10).print_bars('county', 'county_cost', width=80)

::

    county     county_cost
    SEDGWICK    977,174.45 ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    COFFEY      691,749.03 ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    MONTGOMERY  447,581.20 ▓░░░░░░░░░░░░░░░░░░░░░░░░░
    JOHNSON     420,628.00 ▓░░░░░░░░░░░░░░░░░░░░░░░░
    SALINE      245,450.24 ▓░░░░░░░░░░░░░░
    FINNEY      171,862.20 ▓░░░░░░░░░░
    BROWN       145,254.96 ▓░░░░░░░░
    KIOWA        97,974.00 ▓░░░░░
    WILSON       74,747.10 ▓░░░░
    FORD         70,780.00 ▓░░░░
                           +-------------+-------------+-------------+-------------+
                           0          250,000       500,000       750,000  1,000,000

Table of contents
=================

.. toctree::
    :maxdepth: 2

    install
    tutorial
    cookbook
    extensions
    api
    contributing
    release_process

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
