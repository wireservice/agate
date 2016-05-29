#!/usr/bin/env python
# pylint: disable=W0212

import leather

from agate import utils


def dot_chart(self, x, y, path=None, width=None, height=None):
    """
    Render a scatterplot using `leather`.

    :param x:
        The name of a column to plot as the x-axis.
    :param y:
        The name of a column to plot as the y-axis.
    :param path:
        If specified, the resulting SVG will be saved to this location. If
        :code:`None` and running in IPython, then the SVG will be rendered
        inline. Otherwise, the SVG data will be returned as a string.
    :param width:
        The width of the output SVG.
    :param height:
        The height of the output SVG.
    """
    data = tuple(zip(self._columns[x], self._columns[y]))

    chart = leather.Chart()
    chart.add_x_axis(name=x)
    chart.add_y_axis(name=y)
    chart.add_dots(data)

    return chart.to_svg(path, width=width, height=height)
