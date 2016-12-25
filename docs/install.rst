============
Installation
============

Users
-----

To use agate install it with pip::

    pip install agate

.. note::

    Need more speed? Upgrade to Python 3. It's 3-5x faster than Python 2.

    If you must use Python 2 you can you can :code:`pip install cdecimal` for a performance boost.

Developers
----------

If you are a developer that also wants to hack on agate, install it from git::

    git clone git://github.com/onyxfish/agate.git
    cd agate
    mkvirtualenv agate

    # If running Python 3 (strongly recommended for development)
    pip install -r requirements-py3.txt

    # If running Python 2
    pip install -r requirements-py2.txt

    python setup.py develop
    tox

.. note::

    To run the agate tests with coverage::

        nosetests --with-coverage tests

Supported platforms
-------------------

agate supports the following versions of Python:

* Python 2.7
* Python 3.3+
* `PyPy <http://pypy.org/>`_ versions >= 4.0.0

It is tested primarily on OSX, but due to its minimal dependencies it should work perfectly on both Linux and Windows.

.. note::

    `iPython <http://ipython.org/>`_ or `Jupyter <https://jupyter.org/>`_ user? Agate works great there too.
