==============
Modifying data
==============

Computing percent change
========================

You could use :meth:`.Table.compute` to calculate percent change, however, for your convenience journalism has a builtin shortcut 

.. code-block:: python

    new_table = table.percent_change('july', 'august', 'pct_change')

This will compute the percent change between the :code:`july` and :code:`august` columns and put the result in a new :code:`pct_change` column in the resulting table.

Rounding to two decimal places
==============================

journalism stores numerical values using Python's :class:`decimal.Decimal` type. This data type ensures numerical precision beyond what is supported by the native :func:`float` type, however, because of this we can not use Python's builtin :func:`round` function. Instead we must use :meth:`decimal.Decimal.quantize`.

We can use :meth:`.Table.compute` to apply the quantize to generate a rounded column from an existing one:

.. code-block:: python

    from decimal import Decimal
    from journalism import NumberType
    
    number_type = NumberType()

    def round_price(row):
        return row['price'].quantize(Decimal('0.01'))

    new_table = table.compute('price_rounded', number_type, round_price)

To round to one decimal place you would simply change :code:`0.01` to :code:`0.1`.

