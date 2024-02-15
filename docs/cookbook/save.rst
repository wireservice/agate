============
Save a table
============

To a CSV
========

.. code-block:: python

    table.to_csv('filename.csv')

To JSON
=======

.. code-block:: python

    table.to_json('filename.json')

To newline-delimited JSON
=========================

.. code-block:: python

    table.to_json('filename.json', newline=True)

To a SQL database
=================

Use the `agate-sql <https://agate-sql.readthedocs.org/>`_ extension.

.. code-block:: python

    import agatesql

    table.to_sql('postgresql:///database', 'output_table')
