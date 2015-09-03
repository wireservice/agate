=============
Emulating SQL
=============

agate's command structure is very similar to SQL. The primary difference between agate and SQL is that commands like :code:`SELECT` and :code:`WHERE` explicitly create new tables. You can chain them together as you would with SQL, but be aware each command is actually creating a new table.

.. note::

    All examples in this section use the `PostgreSQL <http://www.postgresql.org/>`_ dialect for comparison.

SELECT
======

SQL:

.. code-block:: postgres

    SELECT state, total FROM table;

agate:

.. code-block:: python

    new_table = table.select(('state', 'total'))

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

    joined = patients.inner_join('doctor', doctors, 'id')

LEFT OUTER JOIN
===============

SQL:

.. code-block:: postgres

    SELECT * FROM patient LEFT OUTER JOIN doctor ON (patient.doctor = doctor.id);

agate:

.. code-block:: python

    joined = patients.left_outer_join('doctor', doctors, 'id')

GROUP BY
========

agate's :meth:`.Table.group_by` works slightly different than SQLs. It does not require an aggregate function. Instead it returns :py:class:`.TableSet`. To see how to perform the equivalent of a SQL aggregate, see below.

.. code-block:: python

    doctors = patients.group_by('doctor')

Chaining commands together
==========================

SQL:

.. code-block:: postgres

    SELECT state, total FROM table WHERE LOWER(state) = 'california' ORDER BY total DESC;

agate:

.. code-block:: python

    new_table = table \
        .select(('state', 'total')) \
        .where(lambda row: row['state'].lower() == 'california') \
        .order_by('total', reverse=True)

.. note::

    I don't advise chaining commands like this. Being explicit about each step is usually better.

Aggregate functions
===================

SQL:

.. code-block:: postgres

    SELECT mean(age), median(age) FROM patients GROUP BY doctor;

agate:

.. code-block:: python

    doctors = patients.group_by('doctor')
    patient_ages = doctors.aggregate([
        ('age', agate.Length(), 'patient_count')
        ('age', agate.Mean(), 'age_mean'),
        ('age', agate.Median(), 'age_median')
    ])

The resulting table will have four columns: ``doctor``, ``patient_count``, ``age_mean`` and ``age_median``.
