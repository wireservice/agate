===========
Emulating R
===========

aggregate
=========

R:

.. code-block:: r

    aggregate(employees$salary, list(job = employees$job), mean)

journalism:

.. code-block:: python

    aggregates = employees..aggregate('job', { 'salary': 'mean' })

