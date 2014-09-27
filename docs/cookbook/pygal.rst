===================
Plotting with pygal
===================

`pygal <http://pygal.org/>`_ is a neat library for generating SVG charts. journalism works well with it too.

Line chart
==========

.. code-block:: python

    import pygal

    line_chart = pygal.Line()
    line_chart.title = 'State totals'
    line_chart.x_labels = states.columns['state_abbr']
    line_chart.add('Total', states.columns['total'])
    line_chart.render_to_file('total_by_state.svg') 


