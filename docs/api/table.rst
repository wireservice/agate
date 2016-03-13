=====
Table
=====

.. automodule:: agate.table
    :no-members:

.. autosummary::
    :nosignatures:

    agate.Table

Properties
----------

.. autosummary::
    :nosignatures:

    agate.Table.columns
    agate.Table.column_names
    agate.Table.column_types
    agate.Table.rows
    agate.Table.row_names

Creating tables
---------------

.. autosummary::
    :nosignatures:

    agate.Table.from_csv
    agate.Table.from_json
    agate.Table.from_object

Saving tables
-------------

.. autosummary::
    :nosignatures:

    agate.Table.to_csv
    agate.Table.to_json

Basic processing
----------------

.. autosummary::
    :nosignatures:

    agate.Table.select
    agate.Table.exclude
    agate.Table.where
    agate.Table.find
    agate.Table.limit
    agate.Table.order_by
    agate.Table.distinct

Calculating new data
--------------------

.. autosummary::
    :nosignatures:

    agate.Table.compute
    agate.Table.aggregate

Advanced processing
-------------------

.. autosummary::
    :nosignatures:

    agate.Table.join
    agate.Table.merge
    agate.Table.group_by
    agate.Table.denormalize
    agate.Table.normalize
    agate.Table.pivot
    agate.Table.homogenize
    agate.Table.rename
    agate.Table.bins

Previewing data
---------------

.. autosummary::
    :nosignatures:

    agate.Table.print_structure
    agate.Table.print_table
    agate.Table.print_bars
    agate.Table.print_html
    agate.Table.print_csv
    agate.Table.print_json

Detailed list
-------------

.. autoclass:: agate.Table
    :members:
    :inherited-members:
