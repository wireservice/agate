#!/usr/bin/env python

"""
This module contains the global configuration for agate. Users should use
:function:`.get_option` and :function:`.set_option` to modify the global
configuration.
"""


options = {
    #: Whether or not to use multithreading to speed up CPU-intensive tasks
    'use_threads': True,
    #: How many threads to use, if enabled
    'thread_count': 4,
    #: The minimum number of data points to split into a thread
    'min_thread_size': 5000
}


def get_option(key):
    """
    Get a global configuration option for agate.

    :param key:
        The name of the configuration option.
    """
    return options[key]

def set_option(key, value):
    """
    Set a global configuration option for agate.

    :param key:
        The name of the configuration option.
    :param value:
        The new value to set for the configuration option.
    """
    options[key] = value
