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

    jobs = employees.group_by('job')
    aggregates = jobs.aggregate([
        ( 'salary', 'mean')
    ])
