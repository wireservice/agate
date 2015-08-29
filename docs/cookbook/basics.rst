==========
The basics
==========

You can always use Python's builtin :mod:`csv` to read and write CSV files, but agate also includes shortcuts to save time.

.. note::

    If you have `csvkit <http://csvkit.rtfd.org/>`_ installed, agate will use it instead of Python's builtin :mod:`csv`. The builting module is not unicode-safe for Python 2, so it is strongly suggested that you do install csvkit.

Loading a table from a CSV
==========================

Assuming your file has a single row of headers:

.. code-block:: python

    from agate import Table, TextType, NumberType

    text_type = TextType()
    number_type = NumberType()

    columns = (
        ('city', text_type),
        ('area', number_type),
        ('population', number_type)
    )

    table = Table.from_csv('population.csv', columns)

If your file does not have headers:

.. code-block:: python

    table = Table.from_csv('population.csv', columns, header=False)

Writing a table to a CSV
========================

.. code-block:: python

    table.to_csv('output.csv')
