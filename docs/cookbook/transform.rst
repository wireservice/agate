=========
Transform
=========

Pivot by a single column
========================

The :meth:`.Table.pivot` method is a general process for grouping data by row and, optionally, by column, and then calculating some aggregation for each group. Consider the following table:

+---------+---------+--------+-------+
|  name   | race    | gender | age   |
+=========+=========+========+=======+
|  Joe    | white   | female | 20    |
+---------+---------+--------+-------+
|  Jane   | asian   | male   | 20    |
+---------+---------+--------+-------+
|  Jill   | black   | female | 20    |
+---------+---------+--------+-------+
|  Jim    | latino  | male   | 25    |
+---------+---------+--------+-------+
|  Julia  | black   | female | 25    |
+---------+---------+--------+-------+
|  Joan   | asian   | female | 25    |
+---------+---------+--------+-------+

In the very simplest case, this table can be pivoted to count the number occurences of values in a column:

.. code-block:: python

    transformed = table.pivot('race')

Result:

+---------+--------+
| race    | pivot  |
+=========+========+
| white   | 1      |
+---------+--------+
| asian   | 2      |
+---------+--------+
| black   | 2      |
+---------+--------+
| latino  | 1      |
+---------+--------+

Pivot by multiple columns
=========================

You can pivot by multiple columns either as additional row-groups, or as intersecting columns. For example, given the table in the previous example:

.. code-block:: python

    transformed = table.pivot(['race', 'gender'])

Result:

+---------+--------+-------+
| race    | gender | pivot |
+=========+========+=======+
| white   | female | 1     |
+---------+--------+-------+
| asian   | male   | 1     |
+---------+--------+-------+
| black   | female | 2     |
+---------+--------+-------+
| latino  | male   | 1     |
+---------+--------+-------+
| asian   | female | 1     |
+---------+--------+-------+

For the column, version you would do:

.. code-block:: python

    transformed = table.pivot('race', 'gender')

Result:

+---------+--------+--------+
| race    | male   | female |
+=========+========+========+
| white   | 0      | 1      |
+---------+--------+--------+
| asian   | 1      | 1      |
+---------+--------+--------+
| black   | 0      | 2      |
+---------+--------+--------+
| latino  | 1      | 0      |
+---------+--------+--------+

Pivot to sum
============

The default pivot aggregation is :class:`.Count` but you can also supply other operations. For example, to aggregate each group by :class:`.Sum` of their ages:

.. code-block:: python

    transformed = table.pivot('race', 'gender', aggregation=agate.Sum('age'))

+---------+--------+--------+
| race    | male   | female |
+=========+========+========+
| white   | 0      | 20     |
+---------+--------+--------+
| asian   | 20     | 25     |
+---------+--------+--------+
| black   | 0      | 45     |
+---------+--------+--------+
| latino  | 25     | 0      |
+---------+--------+--------+

Pivot to percent of total
=========================

Pivot allows you to apply a :class:`.Computation` to each row of aggregated results prior to returning the table. Use the stringified name of the aggregation as the column argument to your computation:

.. code-block:: python

    transformed = table.pivot('race', 'gender', aggregation=agate.Sum('age'), computation=agate.Percent('sum'))

+---------+--------+--------+
| race    | male   | female |
+=========+========+========+
| white   | 0      | 14.8   |
+---------+--------+--------+
| asian   | 14.8   | 18.4   |
+---------+--------+--------+
| black   | 0      | 33.3   |
+---------+--------+--------+
| latino  | 18.4   | 0      |
+---------+--------+--------+

*Note: actual computed percentages will be much more precise.*

It's helpful when constructing these cases to think of all the cells in the pivot table as a single sequence.

Denormalize key/value columns into separate columns
===================================================

It's common for very large datasets to be distributed in a "normalized" format, such as:

+---------+-----------+---------+
|  name   | property  | value   |
+=========+===========+=========+
|  Jane   | gender    | female  |
+---------+-----------+---------+
|  Jane   | race      | black   |
+---------+-----------+---------+
|  Jane   | age       | 24      |
+---------+-----------+---------+
|  ...    |  ...      |  ...    |
+---------+-----------+---------+

The :meth:`.Table.denormalize` method can be used to transform the table so that each unique property has its own column.

.. code-block:: python

    transformed = table.denormalize('name', 'property', 'value')

Result:

+---------+----------+--------+-------+
|  name   | gender   | race   | age   |
+=========+==========+========+=======+
|  Jane   | female   | black  | 24    |
+---------+----------+--------+-------+
|  Jack   | male     | white  | 35    |
+---------+----------+--------+-------+
|  Joe    | male     | black  | 28    |
+---------+----------+--------+-------+

Normalize separate columns into key/value columns
=================================================

Sometimes you have a dataset where each property has its own column, but your analysis would be easier if all properties were stored together. Consider this table:

+---------+----------+--------+-------+
|  name   | gender   | race   | age   |
+=========+==========+========+=======+
|  Jane   | female   | black  | 24    |
+---------+----------+--------+-------+
|  Jack   | male     | white  | 35    |
+---------+----------+--------+-------+
|  Joe    | male     | black  | 28    |
+---------+----------+--------+-------+

The :meth:`.Table.normalize` method can be used to transform the table so that all the properties and their values share two columns.

.. code-block:: python

    transformed = table.normalize('name', ['gender', 'race', 'age'])

Result:

+---------+-----------+---------+
|  name   | property  | value   |
+=========+===========+=========+
|  Jane   | gender    | female  |
+---------+-----------+---------+
|  Jane   | race      | black   |
+---------+-----------+---------+
|  Jane   | age       | 24      |
+---------+-----------+---------+
|  ...    |  ...      |  ...    |
+---------+-----------+---------+
