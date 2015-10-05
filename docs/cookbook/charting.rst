================
Rendering charts
================

Using matplotlib
================

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
