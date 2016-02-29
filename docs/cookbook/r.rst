=========
Emulate R
=========

c()
===

Agate's :meth:`.Table.select` and :meth:`.Table.exclude` are the equivalent of R's :code:`c` for selecting columns.

R:

.. code-block:: r

    selected <- data[c("last_name", "first_name", "age")]
    excluded <- data[!c("last_name", "first_name", "age")]

agate:

.. code-block:: python

    selected = table.select(['last_name', 'first_name', 'age'])
    excluded = table.exclude(['last_name', 'first_name', 'age'])

subset
======

Agate's :meth:`.Table.where` is the equivalent of R's :code:`subset`.

R:

.. code-block:: r

    newdata <- subset(data, age >= 20 | age < 10)

agate:

.. code-block:: python

    new_table = table.where(lambda row: row['age'] >= 20 or row['age'] < 10)

order
=====

Agate's :meth:`.Table.order_by` is the equivalent of R's :code:`order`.

R:

.. code-block:: r

    newdata <- employees[order(last_name),]

agate:

.. code-block:: python

    new_table = employees.order_by('last_name')

merge
=====

Agate's :meth:`.Table.join` is the equivalent of R's :code:`merge`.

R:

.. code-block:: r

    joined <- merge(employees, states, by="usps")

agate:

.. code-block:: python

    joined = employees.join(states, 'usps')

rbind
=====

Agate's :meth:`.Table.merge` is the equivalent of R's :code:`rbind`.

R:

.. code-block:: r

    merged <- rbind(first_year, second_year)

agate:

.. code-block:: python

    merged = agate.Table.merge(first_year, second_year)

aggregate
=========

Agate's :meth:`.Table.group_by` and :meth:`.TableSet.aggregate` can be used to recreate the functionality of R's :code:`aggregate`.

R:

.. code-block:: r

    aggregates = aggregate(employees$salary, list(job = employees$job), mean)

agate:

.. code-block:: python

    jobs = employees.group_by('job')
    aggregates = jobs.aggregate([
        ('mean', agate.Mean('salary'))
    ])

melt
====

Agate's :meth:`.Table.normalize` is the equivalent of R's :code:`melt`.

R:

.. code-block:: r

    melt(employees, id=c("last_name", "first_name"))

agate:

.. code-block:: python

    employees.normalize(['last_name', 'first_name'])

cast
====

Agate's :meth:`.Table.denormalize` is the equivalent of R's :code:`cast`.

R:

.. code-block:: r

    melted = melt(employees, id=c("name"))
    casted = cast(melted, name~variable, mean)

agate:

.. code-block:: python

    normalized = employees.normalize(['name'])
    denormalized = normalized.denormalize('name')
