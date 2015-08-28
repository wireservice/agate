==========
The basics
==========

Loading a table from a CSV
==========================

You can use Python's builtin :mod:`csv` to read CSV files.

If your file does not have headers:

.. code-block:: python

    from agate import Table, TextType, NumberType

    text_type = TextType()
    number_type = NumberType()

    columns = (
        ('city', text_type),
        ('area', number_type),
        ('population', number_type)
    )

    with open('population.csv') as f:
        rows = list(csv.reader(f)

    table = Table(rows, columns)

If your file does have headers (and you want to use them):

.. code-block:: python

    with open('population.csv') as f:
        rows = list(csv.reader(f))

    column_names = rows.pop(0)
    column_types = (text_type, number_type, number_type)

    table = Table(rows, zip(column_names, column_types))

Loading a table from a CSV w/ csvkit
====================================

Of course, cool kids use `csvkit <http://csvkit.rtfd.org/>`_. (Hint: it supports unicode!)

.. code-block:: python

    import csvkit

    with open('population.csv') as f:
        rows = list(csvkit.reader(f))

    column_names = rows.pop(0)
    column_types = (text_type, number_type, number_type)

    table = Table(rows, zip(column_names, column_types))

Writing a table to a CSV
========================

.. code-block:: python

    with open('output.csv') as f:
        writer = csv.writer(f)

        writer.writerow(table.get_column_names())
        writer.writerows(table.rows)

Writing a table to a CSV w/ csvkit
==================================

.. code-block:: python

    with open('output.csv') as f:
        writer = csvkit.writer(f)

        writer.writerow(table.get_column_names())
        writer.writerows(table.rows)
