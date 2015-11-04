==========
Statistics
==========

Common descriptive and aggregate statistics are included with the core agate library. For additional statistical methods beyond the scope of agate consider using the `agate-stats <http://agate-stats.rtfd.org/>`_ extension or integrating with `scipy <http://www.scipy.org/>`_.

Descriptive statistics
======================

agate includes a full set of standard descriptive statistics that can be applied to any column containing :class:`.Number` data.

.. code-block:: python

    table.aggregate(Sum('salary'))
    table.aggregate(Min('salary'))
    table.aggregate(Max('salary'))
    table.aggregate(Mean('salary'))
    table.aggregate(Median('salary'))
    table.aggregate(Mode('salary'))
    table.aggregate(Variance('salary'))
    table.aggregate(StDev('salary'))
    table.aggregate(MAD('salary'))

Or, get several at once:

.. code-block:: python

    table.aggregate([
        Min('salary'),
        Mean('salary'),
        Max('salary')
    ])

Aggregate statistics
====================

You can also generate aggregate statistics for subsets of data (sometimes colloquially referred to as "rolling up".

.. code-block:: python

    doctors = patients.group_by('doctor')
    patient_ages = doctors.aggregate([
        ('patient_count', agate.Length())
        ('age_mean', agate.Mean('age')),
        ('age_median', agate.Median('age'))
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
