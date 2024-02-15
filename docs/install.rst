============
Installation
============

Users
-----

To use agate install it with pip::

    pip install agate

For non-English locale support, `install PyICU <https://gitlab.pyicu.org/main/pyicu#installing-pyicu>`__.

Developers
----------

If you are a developer that also wants to hack on agate, install it from git::

    git clone git://github.com/wireservice/agate.git
    cd agate
    mkvirtualenv agate

    pip install -e .[test]

    python setup.py develop

.. note::

    To run the agate tests with coverage::

        pytest --cov agate

Supported platforms
-------------------

agate supports the following versions of Python:

* Python 2.7
* Python 3.5+
* `PyPy <https://www.pypy.org/>`_ versions >= 4.0.0

It is tested primarily on OSX, but due to its minimal dependencies it should work perfectly on both Linux and Windows.

.. note::

    `iPython <https://ipython.org/>`_ or `Jupyter <https://jupyter.org/>`_ user? Agate works great there too.
