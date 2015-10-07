==========
Statistics
==========

Common descriptive and aggregate statistics are included with the core agate library. For additional statistical methods beyond the scope of agate consider using the `agate-stats <http://agate-stats.rtfd.org/>`_ extension or integrating with `scipy <http://www.scipy.org/>`_.

Descriptive statistics
======================

agate includes a full set of standard descriptive statistics that can be applied to any column containing :class:`.Number` data.

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

    doctors = patients.group_by('doctor')
    patient_ages = doctors.aggregate([
        ('age', agate.Length(), 'patient_count')
        ('age', agate.Mean(), 'age_mean'),
        ('age', agate.Median(), 'age_median')
    ])

The resulting table will have four columns: ``doctor``, ``patient_count``, ``age_mean`` and ``age_median``.

Identify outliers
=================

The `agate-stats <http://agate-stats.readthedocs.org/>`_ extension adds methods for finding outliers.

.. code-block:: python

    import agatestats

    agatestats.patch()

    outliers = table.stdev_outliers('salary', deviations=3, reject=False)

By specifying :code:`reject=True` you can instead return a table including only those values **not** identified as outliers.

.. code-block:: python

    not_outliers = table.stdev_outliers('salary', deviations=3, reject=True)

The second, more robust, method for identifying outliers is by identifying values which are more than some number of "median absolute deviations" from the median (typically 3).

.. code-block:: python

    outliers = table.mad_outliers('salary', deviations=3, reject=False)

As with the first example, you can specify :code:`reject=True` to exclude outliers in the resulting table.
