================
Rendering charts
================

Automatic charts
================

Use the `agate-charts <http://agate-charts.readthedocs.org/>`_ extension for fast, exploratory charting:

.. code-block:: python

    import agatecharts

    table.line_chart('x_column_name', 'y_column_name')
    table.bar_chart('label_column_name', ['value_column_name', 'value2_column_name'])
    table.column_chart('label_column_name', 'value_column_name')
    table.scatter_chart('x_column_name', 'y_column_name')

You can also use it to generate small multiples charts from instances of :class:`.TableSet`.

.. code-block:: python

    tableset.line_chart('x_column_name', 'y_column_name')
    tableset.bar_chart('label_column_name', ['value_column_name', 'value2_column_name'])
    tableset.column_chart('label_column_name', 'value_column_name')
    tableset.scatter_chart('x_column_name', 'y_column_name')

Custom charts
=============

If you need more control over charting than is offered by `agate-charts`_ then you can always use agate with `matplotlib <http://matplotlib.org/>`_.

Here is an example of how you might generate a line chart:

.. code-block:: python

    import pylab

    pylab.plot(table.columns['homeruns'], table.columns['wins'])
    pylab.xlabel('Homeruns')
    pylab.ylabel('Wins')
    pylab.title('How homeruns correlate to wins')

    pylab.show()

A similar example that draws a histogram:

.. code-block:: python

    pylab.hist(table.columns['state'])

    pylab.xlabel('State')
    pylab.ylabel('Count')
    pylab.title('Count by state')

    pylab.show()
