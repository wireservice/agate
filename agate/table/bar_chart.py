#!/usr/bin/env python
# pylint: disable=W0212

import leather

from agate import utils


def bar_chart(self, label, value, path=None, width=None, height=None):
    """
    Render a scatterplot using `leather`.

    :param label:
        The name of a column to plot as the labels of the chart.
    :param y:
        The name of a column to plot as the values of the chart.
    :param path:
        If specified, the resulting SVG will be saved to this location. If
        :code:`None` and running in IPython, then the SVG will be rendered
        inline. Otherwise, the SVG data will be returned as a string.
    :param width:
        The width of the output SVG.
    :param height:
        The height of the output SVG.
    """
    data = tuple(zip(self._columns[value], self._columns[label]))

    chart = leather.Chart()
    chart.add_x_axis(name=value)
    chart.add_y_axis(name=label)
    chart.add_bars(data)

    return chart.to_svg(path, width=width, height=height)
