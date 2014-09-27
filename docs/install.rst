============
Installation
============

Users
-----

If you only want to use journalism, install it this way::

    pip install journalism 

.. note::

    Need more speed? If you're running Python 2.6, 2.7 or 3.2, you can :code:`pip install cdecimal` for a significant speed boost. This isn't installed automatically because it can create additional complications.

Developers
----------

If you are a developer that also wants to hack on journalism, install it this way::

    git clone git://github.com/onyxfish/journalism.git
    cd journalism
    mkvirtualenv journalism
    pip install -r requirements.txt
    python setup.py develop
    tox

.. note::

    `requirements.txt` assumes you are using Python 2 as your primary development environment. If you are developing on Python 3, you'll need to `pip install python-dateutil>=2.0` to upgrade to a the correct version.

.. note::

    journalism also supports running tests with coverage:: 

        nosetests --with-coverage --cover-package=journalism

Supported platforms
-------------------

journalism supports the following versions of Python:

* Python 2.6+
* Python 3.2+
* Latest `PyPy <http://pypy.org/>`_

It is tested on OSX, but due to it's minimal dependencies should work fine on both Linux and Windows.

