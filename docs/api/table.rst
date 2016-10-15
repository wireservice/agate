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

Creating
--------

.. autosummary::
    :nosignatures:

    agate.Table.from_csv
    agate.Table.from_json
    agate.Table.from_fixed
    agate.Table.from_object

Saving
------

.. autosummary::
    :nosignatures:

    agate.Table.to_csv
    agate.Table.to_json

Basic processing
----------------

.. autosummary::
    :nosignatures:

    agate.Table.distinct
    agate.Table.exclude
    agate.Table.find
    agate.Table.limit
    agate.Table.order_by
    agate.Table.select
    agate.Table.where

Calculating new data
--------------------

.. autosummary::
    :nosignatures:

    agate.Table.aggregate
    agate.Table.compute

Advanced processing
-------------------

.. autosummary::
    :nosignatures:

    agate.Table.bins
    agate.Table.denormalize
    agate.Table.group_by
    agate.Table.homogenize
    agate.Table.join
    agate.Table.merge
    agate.Table.normalize
    agate.Table.pivot
    agate.Table.rename

Previewing
----------

.. autosummary::
    :nosignatures:

    agate.Table.print_bars
    agate.Table.print_csv
    agate.Table.print_html
    agate.Table.print_json
    agate.Table.print_structure
    agate.Table.print_table

Charting
--------

.. autosummary::
    :nosignatures:

    agate.Table.bar_chart
    agate.Table.column_chart
    agate.Table.line_chart
    agate.Table.scatterplot

Detailed list
-------------

.. autoclass:: agate.Table
    :members:
    :inherited-members:
