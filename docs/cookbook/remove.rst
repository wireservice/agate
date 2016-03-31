==============
Remove columns
==============

Include specific columns
=========================

Create a new table with only a specific set of columns:

.. code-block:: python

    include_columns = ['column_name_one', 'column_name_two']

    new_table = table.select(include_columns)
    
Exclude specific columns
========================

Create a new table without a specific set of columns:

.. code-block:: python

    exclude_columns = ['column_name_one', 'column_name_two']

    new_table = table.exclude(exclude_columns)
