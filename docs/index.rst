====================
journalism |release|
====================

About
=====

.. include:: ../README

Principles
==========

journalism is a intended to fill a very particular programming niche, that of non-professional data analysts who need to get shit done quickly. These are the principles of its development: 

* Humans have less time than computers. Always optimize for humans.
* Most datasets are simple and small. Never optimize for quants.
* Text is data. It must be a first-class citizen.
* Python gets it right. Make it work like Python does. 
* Humans are busy, stupid, lazy, etc. It must be easy.
* Mutability is confusion. Processes that alter data must create new copies.

But why not...

* numpy: It's hard.
* pandas: It's hard.
* R: Don't even get me started.
* SAS: You have that kind of money?
* SQL: It's not code.
* An ORM: Have you actually tried this?

I'm not reinventing the wheel, I'm just putting on the right size tires.

Installation
============

Users
-----

If you only want to use journalism, install it this way::

    pip install journalism 

Developers
----------

If you are a developer that also wants to hack on journalism, install it this way::

    git clone git://github.com/onyxfish/journalism.git
    cd journalism
    mkvirtualenv --no-site-packages journalism
    pip install -r requirements.txt
    python setup.py develop
    nosetests

Usage
=====

Here is an example of how to use journalism::

    TODO 

Contributing
============

Want to hack on journalism? Here's how:

.. toctree::
    :maxdepth: 2

    contributing

Authors
=======

.. include:: ../AUTHORS

License
=======

.. include:: ../COPYING

Changelog
=========

.. include:: ../CHANGELOG

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

