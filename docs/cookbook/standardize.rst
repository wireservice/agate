============================
Standardize names and values
============================

Standardize row and columns names
=================================

The :meth:`Table.rename` method has arguments to convert row or column names to slugs and append unique identifiers to duplicate values.

Using an existing table object:

.. code-block:: python

    # Convert column names to unique slugs
    table.rename(slug_columns=True)

    # Convert row names to unique slugs
    table.rename(slug_rows=True)

    # Convert both column and row names to unique slugs
    table.rename(slug_columns=True, slug_rows=True)

Standardize column values
=========================

agate has a :class:`Slug` computation that can be used to also standardize text column values. The computation has an option to also append unique identifiers to duplicate values.

Using an existing table object:

.. code-block:: python

    # Convert the values in column 'title' to slugs
    new_table = table.compute([
        ('title-slug', agate.Slug('title'))
    ])
    
    # Convert the values in column 'title' to unique slugs
    new_table = table.compute([
        ('title-slug', agate.Slug('title', ensure_unique=True))
    ])
