=====================
CSV reader and writer
=====================

Agate contains CSV readers and writers that are intended to be used as a drop-in replacement for :mod:`csv`. These versions add unicode support for Python 2 and several other minor features.

Agate methods will use these version automatically. If you would like to use them in your own code, you can import them, like this:

.. code-block:: python

    from agate import csv

Due to nuanced differences between the versions, these classes are implemented seperately for Python 2 and Python 3. The documentation for both versions is provided below, but only the one for your version of Python is imported with the above code.

Python 3
--------

.. autosummary::
    :nosignatures:

    agate.csv_py3.reader
    agate.csv_py3.writer
    agate.csv_py3.Reader
    agate.csv_py3.Writer
    agate.csv_py3.DictReader
    agate.csv_py3.DictWriter

Python 3 details
----------------

.. autofunction:: agate.csv_py3.reader
.. autofunction:: agate.csv_py3.writer
.. autoclass:: agate.csv_py3.Reader
.. autoclass:: agate.csv_py3.Writer
.. autoclass:: agate.csv_py3.DictReader
.. autoclass:: agate.csv_py3.DictWriter
