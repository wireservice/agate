===========
Emulating R
===========

aggregate
=========

R:

.. code-block:: r

    aggregate(employees$salary, list(job = employees$job), mean)

agate:

.. code-block:: python

    jobs = employees.group_by('job')
    aggregates = jobs.aggregate([
        ( 'salary', 'mean')
    ])
