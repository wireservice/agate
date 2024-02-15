==========
Statistics
==========

Common descriptive and aggregate statistics are included with the core agate library. For additional statistical methods beyond the scope of agate consider using the `agate-stats <https://agate-stats.rtfd.org/>`_ extension or integrating with `scipy <https://scipy.org/>`_.

Descriptive statistics
======================

agate includes a full set of standard descriptive statistics that can be applied to any column containing :class:`.Number` data.

.. code-block:: python

    table.aggregate(agate.Sum('salary'))
    table.aggregate(agate.Min('salary'))
    table.aggregate(agate.Max('salary'))
    table.aggregate(agate.Mean('salary'))
    table.aggregate(agate.Median('salary'))
    table.aggregate(agate.Mode('salary'))
    table.aggregate(agate.Variance('salary'))
    table.aggregate(agate.StDev('salary'))
    table.aggregate(agate.MAD('salary'))

Or, get several at once:

.. code-block:: python

    table.aggregate([
        ('salary_min', agate.Min('salary')),
        ('salary_ave', agate.Mean('salary')),
        ('salary_max', agate.Max('salary')),
    ])

Aggregate statistics
====================

You can also generate aggregate statistics for subsets of data (sometimes referred to as "rolling up"):

.. code-block:: python

    doctors = patients.group_by('doctor')
    patient_ages = doctors.aggregate([
        ('patient_count', agate.Count()),
        ('age_mean', agate.Mean('age')),
        ('age_median', agate.Median('age'))
    ])

The resulting table will have four columns: ``doctor``, ``patient_count``, ``age_mean`` and ``age_median``.

You can roll up by multiple columns by chaining agate's :meth:`.Table.group_by` method.

.. code-block:: python

    doctors_by_state = patients.group_by("state").group_by('doctor')

Distribution by count (frequency)
=================================

Counting the number of each unique value in a column can be accomplished with the :meth:`.Table.pivot` method:

.. code-block:: python

    # Counts of a single column's values
    table.pivot('doctor')

    # Counts of all combinations of more than one column's values
    table.pivot(['doctor', 'hospital'])

The resulting tables will have a column for each key column and another :code:`Count` column counting the number of instances of each value.

Distribution by percent
=======================

:meth:`.Table.pivot` can also be used to calculate the distribution of values as a percentage of the total number:

.. code-block:: python

    # Percents of a single column's values
    table.pivot('doctor', computation=agate.Percent('Count'))

    # Percents of all combinations of more than one column's values
    table.pivot(['doctor', 'hospital'], computation=agate.Percent('Count'))

The output table will be the same format as the previous example, except the value column will be named :code:`Percent`.

Identify outliers
=================

The `agate-stats <https://agate-stats.rtfd.org/>`_ extension adds methods for finding outliers.

.. code-block:: python

    import agatestats

    outliers = table.stdev_outliers('salary', deviations=3, reject=False)

By specifying :code:`reject=True` you can instead return a table including only those values **not** identified as outliers.

.. code-block:: python

    not_outliers = table.stdev_outliers('salary', deviations=3, reject=True)

The second, more robust, method for identifying outliers is by identifying values which are more than some number of "median absolute deviations" from the median (typically 3).

.. code-block:: python

    outliers = table.mad_outliers('salary', deviations=3, reject=False)

As with the first example, you can specify :code:`reject=True` to exclude outliers in the resulting table.

Custom statistics
==================

You can also generate custom aggregated statistics for your data by defining your own 'summary' aggregation. This might be especially useful for performing calculations unique to your data. Here's a simple example:

.. code-block:: python

    # Create a custom summary aggregation with agate.Summary
    # Input a column name, a return data type and a function to apply on the column
    count_millionaires = agate.Summary('salary', agate.Number(), lambda r: sum(salary > 1000000 for salary in r.values()))

    table.aggregate([
        count_millionaires
    ])

Your custom aggregation can be used to determine both descriptive and aggregate statistics shown above.
