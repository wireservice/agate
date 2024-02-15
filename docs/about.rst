===========
About agate
===========

Why agate?
==========

* A readable and user-friendly API.
* A complete set of SQL-like operations.
* Unicode support everywhere.
* Decimal precision everywhere.
* Exhaustive user documentation.
* Pluggable `extensions <extensions>`_ that add SQL integration, Excel support, and more.
* Designed with `iPython <https://ipython.org/>`_, `Jupyter <https://jupyter.org/>`_ and `atom/hydrogen <https://atom.io/packages/hydrogen>`_ in mind.
* Pure Python. No C dependencies to compile.
* Exhaustive test coverage.
* MIT licensed and free for all purposes.
* Zealously `zen <https://www.python.org/dev/peps/pep-0020/>`_.
* Made with love.

Principles
==========

agate is a intended to fill a very particular programming niche. It should not be allowed to become as complex as `numpy <https://numpy.org/>`_ or `pandas <https://pandas.pydata.org/>`_. Please bear in mind the following principles when considering a new feature:

* Humans have less time than computers. Optimize for humans.
* Most datasets are small. Don't optimize for "big data".
* Text is data. It must always be a first-class citizen.
* Python gets it right. Make it work like Python does.
* Humans lives are nasty, brutish and short. Make it easy.
* Mutability leads to confusion. Processes that alter data must create new copies.
* Extensions are the way. Don't add it to core unless everybody needs it.
