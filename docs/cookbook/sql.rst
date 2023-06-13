===========
Emulate SQL
===========

agate's command structure is very similar to SQL. The primary difference between agate and SQL is that commands like :code:`SELECT` and :code:`WHERE` explicitly create new tables. You can chain them together as you would with SQL, but be aware each command is actually creating a new table.

.. note::

    All examples in this section use the `PostgreSQL <https://www.postgresql.org/>`_ dialect for comparison.

If you want to read and write data from SQL, see :ref:`load_a_table_from_a_sql_database`.

SELECT
======

SQL:

.. code-block:: postgres

    SELECT state, total FROM table;

agate:

.. code-block:: python

    new_table = table.select(['state', 'total'])

WHERE
=====

SQL:

.. code-block:: postgres

    SELECT * FROM table WHERE LOWER(state) = 'california';

agate:

.. code-block:: python

    new_table = table.where(lambda row: row['state'].lower() == 'california')

ORDER BY
========

SQL:

.. code-block:: postgres

    SELECT * FROM table ORDER BY total DESC;

agate:

.. code-block:: python

    new_table = table.order_by(lambda row: row['total'], reverse=True)

DISTINCT
========

SQL:

.. code-block:: postgres

    SELECT DISTINCT ON (state) * FROM table;

agate:

.. code-block:: python

    new_table = table.distinct('state')

.. note::

    Unlike most SQL implementations, agate always returns the full row. Use :meth:`.Table.select` if you want to filter the columns first.

INNER JOIN
==========

SQL (two ways):

.. code-block:: postgres

    SELECT * FROM patient, doctor WHERE patient.doctor = doctor.id;

    SELECT * FROM patient INNER JOIN doctor ON (patient.doctor = doctor.id);

agate:

.. code-block:: python

    joined = patients.join(doctors, 'doctor', 'id', inner=True)

LEFT OUTER JOIN
===============

SQL:

.. code-block:: postgres

    SELECT * FROM patient LEFT OUTER JOIN doctor ON (patient.doctor = doctor.id);

agate:

.. code-block:: python

    joined = patients.join(doctors, 'doctor', 'id')

FULL OUTER JOIN
===============

SQL:

.. code-block:: postgres

    SELECT * FROM patient FULL OUTER JOIN doctor ON (patient.doctor = doctor.id);

agate:

.. code-block:: python

    joined = patients.join(doctors, 'doctor', 'id', full_outer=True)

GROUP BY
========

agate's :meth:`.Table.group_by` works slightly different than SQLs. It does not require an aggregate function. Instead it returns :py:class:`.TableSet`. To see how to perform the equivalent of a SQL aggregate, see below.

.. code-block:: python

    doctors = patients.group_by('doctor')

You can group by two or more columns by chaining the command.

.. code-block:: python

    doctors_by_state = patients.group_by('state').group_by('doctor')

HAVING
======

agate's :meth:`.TableSet.having` works very similar to SQL's keyword of the same name.

.. code-block:: python

    doctors = patients.group_by('doctor')
    popular_doctors = doctors.having([
        ('patient_count', Count())
    ], lambda t: t['patient_count'] > 100)

This filters to only those doctors whose table includes at least 100 results. Can add as many aggregations as you want to the list and each will be available, by name in the test function you pass.

For example, here we filter to popular doctors with more an average review of at least three stars:

.. code-block:: python

    doctors = patients.group_by('doctor')
    popular_doctors = doctors.having([
        ('patient_count', Count()),
        ('average_stars', Average('stars'))
    ], lambda t: t['patient_count'] > 100 and t['average_stars'] >= 3)

Chain commands together
=======================

SQL:

.. code-block:: postgres

    SELECT state, total FROM table WHERE LOWER(state) = 'california' ORDER BY total DESC;

agate:

.. code-block:: python

    new_table = table \
        .select(['state', 'total']) \
        .where(lambda row: row['state'].lower() == 'california') \
        .order_by('total', reverse=True)

.. note::

    Chaining commands in this way is sometimes not a good idea. Being explicit about each step can lead to clearer code.

Aggregate functions
===================

SQL:

.. code-block:: postgres

    SELECT mean(age), median(age) FROM patients GROUP BY doctor;

agate:

.. code-block:: python

    doctors = patients.group_by('doctor')
    patient_ages = doctors.aggregate([
        ('patient_count', agate.Count()),
        ('age_mean', agate.Mean('age')),
        ('age_median', agate.Median('age'))
    ])

The resulting table will have four columns: ``doctor``, ``patient_count``, ``age_mean`` and ``age_median``.
