#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains the global configuration for agate. Users should use
:function:`.get_option` and :function:`.set_option` to modify the global
configuration.
"""

from babel.core import default_locale


_options = {
    #: Default locale for number formatting
    'default_locale': default_locale('LC_NUMERIC') or 'en_US',
    #: Character to render for horizontal lines
    'horizontal_line_char': u'-',
    #: Character to render for vertical lines
    'vertical_line_char': u'|',
    #: Character to render for bar chart units
    'bar_char': u'░',
    #: Printable character to render for bar chart units
    'printable_bar_char': u':',
    #: Character to render for zero line units
    'zero_line_char': u'▓',
    #: Printable character to render for zero line units
    'printable_zero_line_char': u'|',
    #: Character to render for axis ticks
    'tick_char': u'+',
    #: Characters to render for ellipsis
    'ellipsis_chars': u'...',
}


def get_option(key):
    """
    Get a global configuration option for agate.

    :param key:
        The name of the configuration option.
    """
    return _options[key]


def set_option(key, value):
    """
    Set a global configuration option for agate.

    :param key:
        The name of the configuration option.
    :param value:
        The new value to set for the configuration option.
    """
    _options[key] = value


def set_options(options):
    """
    Set a dictionary of options simultaneously.

    :param hash:
        A dictionary of option names and values.
    """
    _options.update(options)
