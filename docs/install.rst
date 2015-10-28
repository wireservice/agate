============
Installation
============

Users
-----

If you only want to use agate, install it this way::

    pip install agate

.. note::

    Need more speed? If you're running Python 2.6 or 2.7 or you can :code:`pip install cdecimal` for a significant speed boost. This isn't installed automatically because it can create additional complications.

Developers
----------

If you are a developer that also wants to hack on agate, install it this way::

    git clone git://github.com/onyxfish/agate.git
    cd agate
    mkvirtualenv agate

    # If running Python 2
    pip install -r requirements-py2.txt

    # If running Python 3
    pip install -r requirements-py3.txt

    python setup.py develop
    tox

.. note::

    agate also supports running tests with coverage::

        nosetests --with-coverage --cover-package=agate tests

Supported platforms
-------------------

agate supports the following versions of Python:

* Python 2.6 (provisional support: agate's tests pass, but some dependencies claim not to support it)
* Python 2.7
* Python 3.3+
* `PyPy <http://pypy.org/>`_

It is tested on OSX, but due to its minimal dependencies should work fine on both Linux and Windows.

.. note::

    `iPython <http://ipython.org/>`_ or `Jupyter <https://jupyter.org/>`_ user? Agate works great there too.
