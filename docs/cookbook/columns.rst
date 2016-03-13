===============================
Renaming and reordering columns
===============================

Rename columns
===============

You can rename the columns in a table by using the :meth:`.Table.rename` method and specifying the new column names as an array or dictionary mapping old column names to new ones.

.. code-block:: python

    table = Table(rows, column_names = ['a', 'b', 'c'])
    new_table = table.rename(column_names = ['one', 'two', 'three'])
    # or
    new_table = table.rename(column_names = {'a': 'one', 'b': 'two', 'c': 'three'})

Reorder columns
===============

You can reorder the columns in a table by using the :meth:`.Table.select` method and specifying the column names in the order you want:

.. code-block:: python

    new_table = table.select(['3rd_column_name', '1st_column_name', '2nd_column_name'])
