===============
Homogenize rows
===============

Fill in missing rows in a series. This can be used, for instance, to add rows for missing years in a time series.

Create rows for missing values
==============================

We can insert a default row for each value that is missing in a table from a given sequence of values.

Starting with a table like this, we can fill in rows for all missing years:

+-------+--------------+------------+
|  year | female_count | male_count |
+=======+==============+============+
|  1997 |           2  |         1  |
+-------+--------------+------------+
|  2000 |           4  |         3  |
+-------+--------------+------------+
|  2002 |           4  |         5  |
+-------+--------------+------------+
|  2003 |           1  |         2  |
+-------+--------------+------------+

.. code-block:: python

    key = 'year'
    expected_values = (1997, 1998, 1999, 2000, 2001, 2002, 2003)

    # Your default row should specify column values not in `key`
    default_row = (0, 0)

    new_table = table.homogenize(key, expected_values, default_row)

The result will be:

+-------+--------------+------------+
|  year | female_count | male_count |
+=======+==============+============+
|  1997 |           2  |         1  |
+-------+--------------+------------+
|  1998 |           0  |         0  |
+-------+--------------+------------+
|  1999 |           0  |         0  |
+-------+--------------+------------+
|  2000 |           4  |         3  |
+-------+--------------+------------+
|  2001 |           0  |         0  |
+-------+--------------+------------+
|  2002 |           4  |         5  |
+-------+--------------+------------+
|  2003 |           1  |         2  |
+-------+--------------+------------+


Create dynamic rows based on missing values
===========================================

We can also specify new row values with a value-generating function:

.. code-block:: python

    key = 'year'
    expected_values = (1997, 1998, 1999, 2000, 2001, 2002, 2003)

    # If default row is a function, it should return a full row
    def default_row(missing_value):
      return (missing_value, missing_value-1997, missing_value-1997)

    new_table = table.homogenize(key, expected_values, default_row)

The new table will be:

+-------+--------------+------------+
|  year | female_count | male_count |
+=======+==============+============+
|  1997 |           2  |         1  |
+-------+--------------+------------+
|  1998 |           1  |         1  |
+-------+--------------+------------+
|  1999 |           2  |         2  |
+-------+--------------+------------+
|  2000 |           4  |         3  |
+-------+--------------+------------+
|  2001 |           4  |         4  |
+-------+--------------+------------+
|  2002 |           4  |         5  |
+-------+--------------+------------+
|  2003 |           1  |         2  |
+-------+--------------+------------+
