==========
Statistics
==========

Descriptive statistics
======================

journalism includes a full set of standard descriptive statistics that can be applied to any :class:`.NumberColumn`.

.. code-block:: python

    column = table.columns['salary']

    column.sum()
    column.min()
    column.max()
    column.mean()
    column.median()
    column.mode()
    column.variance()
    column.stdev()
    column.mad()

Aggregate statistics
====================

You can also generate aggregate statistics for subsets of data (sometimes colloquially referred to as "rolling up".

.. code-block:: python

    summary = table.aggregate('profession', { 'salary': 'mean', 'salary': 'median' }) 

A "count" column is always return in the results. The :code:`summary` table in this example would have these columns: :code:`('profession', 'profession_count', 'salary_mean', 'salary_median')`.

Identifying outliers
====================

journalism includes two builtin methods for identifying outliers. The first, and most widely known, is by identifying values which are more than some number of standard deviations from the mean (typically 3).

.. code-block:: python

    outliers = table.stdev_outliers('salary', deviations=3, reject=False)

By specifying :code:`reject=True` you can instead return a table including only those values **not** identified as outliers.

.. code-block:: python

    not_outliers = table.stdev_outliers('salary', deviations=3, reject=True)

The second, more robust, method for identifying outliers is by identifying values which are more than some number of "median absolute deviations" from the median (typically 3).

.. code-block:: python

    outliers = table.mad_outliers('salary', deviations=3, reject=False)

As with the first example, you can specify :code:`reject=True` to exclude outliers in the resulting table.


