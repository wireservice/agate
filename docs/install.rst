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

    journalism also supports running tests with coverage:: 

        nosetests --with-coverage --cover-package=journalism

Supported platforms
-------------------

journalism supports the following versions of Python:

* Python 2.6+
* Python 3.2+
* Latest `PyPy <http://pypy.org/>`_

It is tested on OSX, but due to it's minimal dependencies should work fine on both Linux and Windows.

