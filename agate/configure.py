#!/usr/bin/env python

"""
This module contains the global configuration for agate. Users should use
:function:`.get_option` and :function:`.set_option` to modify the global
configuration.
"""

from concurrent import futures


options = {
    #: Executor to use for parallelizing tasks, or :code:`None` to disable
    'parallel_executor': futures.ThreadPoolExecutor,
    #: How many threads/proceses to use, if enabled
    'parallel_workers': 4,
    #: The minimum number of data points to split into a thread/process
    'parallel_min_size': 5000
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
