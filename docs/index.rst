===============
agate |release|
===============

.. include:: ../README.rst

.. toctree::
    :hidden:
    :maxdepth: 2

    about
    install
    tutorial
    cookbook
    extensions
    api
    contributing
    release_process
    license
    changelog

Show me docs
============

* `About <about.html>`_ - why you should use agate and the principles that guide its development
* `Install <install.html>`_ - how to install for users and developers
* `Tutorial <tutorial.html>`_ - a step-by-step guide to start using agate
* `Cookbook <cookbook.html>`_ - sample code showing how to accomplish dozens of common tasks, including comparisons to SQL, R, etc.
* `Extensions <extensions.html>`_ - a list of libraries that extend agate functionality and how to build your own
* `API <api.html>`_ - technical documentation for every agate feature
* `Changelog <changelog.html>`_ - a record of every change made to agate for each release

Show me code
============

.. code-block:: python

    import agate

    purchases = agate.Table.from_csv('examples/realdata/ks_1033_data.csv')

    by_county = purchases.group_by('county')

    totals = by_county.aggregate([
        ('county_cost', agate.Sum('total_cost'))
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

This example, along with detailed comments, are available as a `Jupyter notebook <https://github.com/wireservice/agate/blob/master/example.py.ipynb>`_.

Join us
=======

* `Contributing <contributing.html>`_ - guidance for developers who want to contribute to agate
* `Release process <release_process.html>`_ - the process for maintainers to publish new releases
* `License <license.html>`_ - a copy of the MIT open source license covering agate

Who we are
==========

.. include:: ../AUTHORS.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
