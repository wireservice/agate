======
Lookup
======

Generate new columns by mapping existing data to common `lookup <https://github.com/wireservice/lookup>`_ tables.

CPI deflation
=============

The `agate-lookup <https://github.com/wireservice/agate-lookup>`_ extension adds a ``lookup`` method to agate's Table class.

Starting with a table that looks like this:

+-------+-------+
|  year | cost  |
+=======+=======+
|  1995 |  2.0  |
+-------+-------+
|  1997 |  2.2  |
+-------+-------+
|  1996 |  2.3  |
+-------+-------+
|  2003 |  4.0  |
+-------+-------+
|  2007 |  5.0  |
+-------+-------+
|  2005 |  6.0  |
+-------+-------+

We can map the ``year`` column to its annual CPI index in one lookup call.

.. code-block:: python

    import agatelookup

    join_year_cpi = table.lookup('year', 'cpi')

The return table will have now have a new column:

+-------+------+----------+
|  year | cost |     cpi  |
+=======+======+==========+
|  1995 |  2.0 | 152.383  |
+-------+------+----------+
|  1997 |  2.2 | 160.525  |
+-------+------+----------+
|  1996 |  2.3 | 156.858  |
+-------+------+----------+
|  2003 |  4.0 | 184.000  |
+-------+------+----------+
|  2007 |  5.0 | 207.344  |
+-------+------+----------+
|  2005 |  6.0 | 195.267  |
+-------+------+----------+

A simple computation tacked on to this lookup can then get the 2015 equivalent values of each cost:

.. code-block:: python
    
    cpi_2015 = Decimal(216.909)

    def cpi_adjust_2015(row):
        return (row['cost'] * (cpi_2015 / row['cpi'])).quantize(Decimal('0.01'))

    cost_2015 = join_year_cpi.compute([
        ('cost_2015', agate.Formula(agate.Number(), cpi_adjust_2015))
    ])
    
And the final table will look like this:

+-------+------+---------+------------+
|  year | cost |     cpi | cost_2015  |
+=======+======+=========+============+
|  1995 |  2.0 | 152.383 |      2.85  |
+-------+------+---------+------------+
|  1997 |  2.2 | 160.525 |      2.97  |
+-------+------+---------+------------+
|  1996 |  2.3 | 156.858 |      3.18  |
+-------+------+---------+------------+
|  2003 |  4.0 | 184.000 |      4.72  |
+-------+------+---------+------------+
|  2007 |  5.0 | 207.344 |      5.23  |
+-------+------+---------+------------+
|  2005 |  6.0 | 195.267 |      6.66  |
+-------+------+---------+------------+
