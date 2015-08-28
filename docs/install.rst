============
Installation
============

Users
-----

If you only want to use agate, install it this way::

    pip install agate

.. note::

    Need more speed? If you're running Python 2.6, 2.7 or 3.2, you can :code:`pip install cdecimal` for a significant speed boost. This isn't installed automatically because it can create additional complications.

Developers
----------

If you are a developer that also wants to hack on agate, install it this way::

    git clone git://github.com/onyxfish/agate.git
    cd agate
    mkvirtualenv agate
    pip install -r requirements.txt
    python setup.py develop
    tox

.. note::

    agate also supports running tests with coverage::

        nosetests --with-coverage --cover-package=agate

Supported platforms
-------------------

agate supports the following versions of Python:

* Python 2.6+
* Python 3.2+
* Latest `PyPy <http://pypy.org/>`_

It is tested on OSX, but due to it's minimal dependencies should work fine on both Linux and Windows.
