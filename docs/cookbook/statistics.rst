==========
Statistics
==========

Descriptive statistics
======================

agate includes a full set of standard descriptive statistics that can be applied to any :class:`.NumberColumn`.

.. code-block:: python

    column = table.columns['salary']

    column.aggregate(Sum())
    column.aggregate(Min())
    column.aggregate(Max())
    column.aggregate(Mean())
    column.aggregate(Median())
    column.aggregate(Mode())
    column.aggregate(Variance())
    column.aggregate(StDev())
    column.aggregate(MAD())

Aggregate statistics
====================

You can also generate aggregate statistics for subsets of data (sometimes colloquially referred to as "rolling up".

.. code-block:: python

    professions = data.group_by('profession')
    summary = professions.aggregate([
        ('salary', 'mean'),
        ('salary', 'median')
    ])

The ``summary`` table will have four columns: ``group`` (the profession), ``count`` (the number of grouped rows), ``salary_mean`` and ``salary_median`` (the aggregates).

Identifying outliers
====================

agate includes two builtin methods for identifying outliers. The first, and most widely known, is by identifying values which are more than some number of standard deviations from the mean (typically 3).

.. code-block:: python

    outliers = table.stdev_outliers('salary', deviations=3, reject=False)

By specifying :code:`reject=True` you can instead return a table including only those values **not** identified as outliers.

.. code-block:: python

    not_outliers = table.stdev_outliers('salary', deviations=3, reject=True)

The second, more robust, method for identifying outliers is by identifying values which are more than some number of "median absolute deviations" from the median (typically 3).

.. code-block:: python

    outliers = table.mad_outliers('salary', deviations=3, reject=False)

As with the first example, you can specify :code:`reject=True` to exclude outliers in the resulting table.
