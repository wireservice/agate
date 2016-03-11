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

* `About <about.html>`_ - why you should use agate and principles behind its implementation
* `Install <install.html>`_ - how to install for users and developers 
* `Tutorial <tutorial.html>`_ - a step-by-step guide to start using agate
* `Cookbook <cookbook.html>`_ - a list of use cases for new users, users coming from other tools and advanced users
* `Extensions <extensions.html>`_ - how to make your own agate extensions and a list of existing extensions
* `API <api.html>`_ - the technical documentation for every agate class and method in the source code

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

This example, complete with a detailed explanation, is available as a `Jupyter notebook <http://nbviewer.ipython.org/urls/gist.githubusercontent.com/onyxfish/36f459dab02545cbdce3/raw/534698388e5c404996a7b570a7228283344adbb1/example.py.ipynb>`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
