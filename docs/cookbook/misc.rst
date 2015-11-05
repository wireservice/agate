=============
Miscellaneous
=============

Reorder columns
===============

You can reorder the columns in a table by using the :meth:`.Table.select` method and specifying the column names in the order you want:

.. code-block:: python

    new_table = table.select(['3rd_column_name', '1st_column_name', '2nd_column_name'])
