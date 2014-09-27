=============
Emulating SQL
=============

journalism's command structure is very similar to SQL. The primary difference between journalism and SQL is that commands like :code:`SELECT` and :code:`WHERE` explicitly create new tables. You can chain them together as you would with SQL, but be aware each command is actually creating a new table.

.. note::

    All examples in this section use the `PostgreSQL <http://www.postgresql.org/>`_ dialect for comparison.

SELECT
======

SQL:

.. code-block:: postgres

    SELECT state, total FROM table;

journalism:

.. code-block:: python

    new_table = table.select(('state', 'total'))

WHERE
=====

SQL:

.. code-block:: postgres

    SELECT * FROM table WHERE LOWER(state) = 'california';

journalism:

.. code-block:: python

    new_table = table.where(lambda row: row['state'].lower() == 'california')

ORDER BY
========

SQL:

.. code-block:: postgres 

    SELECT * FROM table ORDER BY total DESC;

journalism:

.. code-block:: python

    new_table = table.order_by(lambda row: row['total'], reverse=True)

DISTINCT
========

SQL:

.. code-block:: postgres

    SELECT DISTINCT ON (state) * FROM table;

journalism:

.. code-block:: python

    new_table = table.distinct('state')

.. note::

    Unlike most SQL implementations, journalism always returns the full row. Use :meth:`.Table.select` if you want to filter the columns first.

INNER JOIN
==========

SQL (two ways):

.. code-block:: postgres

    SELECT * FROM patient, doctor WHERE patient.doctor = doctor.id;

    SELECT * FROM patient INNER JOIN doctor ON (patient.doctor = doctor.id);

journalism:

.. code-block:: python

    joined = patients.inner_join('doctor', doctors, 'id')

LEFT OUTER JOIN
===============

SQL:

.. code-block:: postgres

    SELECT * FROM patient LEFT OUTER JOIN doctor ON (patient.doctor = doctor.id);

journalism:

.. code-block:: python

    joined = patients.left_outer_join('doctor', doctors, 'id')

GROUP BY
========

journalism's :meth:`.Table.group_by` works slightly different than SQLs. It does not require an aggregate function. Instead it returns a dictionary of :code:`group`, :meth:`.Table` pairs. To see how to perform the equivalent of a SQL aggregate, see the next example.

.. code-block:: python

    groups = patients.group_by('doctor')

Chaining commands together
==========================

SQL:

.. code-block:: postgres

    SELECT state, total FROM table WHERE LOWER(state) = 'california' ORDER BY total DESC;

journalism:

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

    SELECT mean(age) FROM patient GROUP BY doctor;

journalism:

.. code-block:: python

    new_table = patient.aggregate('doctor', { 'age': 'mean' })


