==================
Fixed-width reader
==================

Agate contains a fixed-width file reader that is designed to work like Python's :mod:`csv`.

These readers work with CSV-formatted schemas, such as those maintained at `wireservice/ffs <https://github.com/wireservice/ffs>`_.

.. autosummary::
    :nosignatures:

    agate.fixed.reader
    agate.fixed.Reader
    agate.fixed.DictReader

Detailed list
-------------

.. autofunction:: agate.fixed.reader
.. autoclass:: agate.fixed.Reader
.. autoclass:: agate.fixed.DictReader
