==========================
Contributing to agate
==========================

Principles
==========

agate is a intended to fill a very particular programming niche. It should not be allowed to become as complex as `numpy <http://www.numpy.org/>`_ or `pandas <http://pandas.pydata.org/>`_. Please bear in mind the following principles when contemplating an addition:

* Humans have less time than computers. Always optimize for humans.
* Most datasets are small and simple. Never optimize for "big data".
* Text is data. It must always be a first-class citizen.
* Python gets it right. Make it work like Python does.
* Humans lives are nasty, brutish and short. Make things easy.
* Mutability leads to confusion. Processes that alter data must create new copies.

How agate works
===============

Here are a few notes regarding agate's internal architecture for interested developers. Users shouldn't need to care about these things.

* Methods on :class:`.Table` instances such as :meth:`.Table.select`, :meth:`.Table.where` and :meth:`.Table.order_by` return new :class:`.Table` instances.

* Operations on :class:`.Column` instances access data from their parent :class:`.Table` and return appropriate native data structures. Columns are not portable between instances of :class:`.Table`!

* When a :class:`.Table` is instantiated the data provided is copied into a tuple so that it becomes immutable within the context of the :class:`.Table`.

* :class:`.Table` instances that are "forked" (created by table operations) will share :class:`.Row` instances for memory efficiency. This is safe because row data is immutable. Methods that create new data will copy the row data first. (e.g. :meth:`.Table.compute`)

* :class:`.ColumnMapping`, :class:`.RowSequence`, :class:`.Column`, and :class:`.Row` have **read only** access to a Table's private variables. They are purely a formal abstraction and for purposes of encapsulation they can be treated as a single unit.

* :class:`.Column` instances lazily construct a copy of their data from their parent Table and then cache it. They will also cache the result of common operations such as filtering null values. This caching is safe because the underlying data is immutable.

Process for contributing code
=============================

Contributors should use the following roadmap to guide them through the process of submitting a contribution:

#. Fork the project on `Github <https://github.com/onyxfish/agate>`_.
#. Check out the `issue tracker <https://github.com/onyxfish/agate/issues>`_ and find a task that needs to be done and is of a scope you can realistically expect to complete in a few days. Don't worry about the priority of the issues at first, but try to choose something you'll enjoy. You're much more likely to finish something to the point it can be merged if it's something you really enjoy hacking on.
#. Comment on the ticket letting everyone know you're going to be hacking on it so that nobody duplicates your effort. It's also good practice to provide some general idea of how you plan on resolving the issue so that other developers can make suggestions.
#. Write tests for the feature you're building. Follow the format of the existing tests in the test directory to see how this works. You can run all the tests with the command ``nosetests``. (Or ``tox`` to run across all versions of Python.)
#. Write the code. Try to stay consistent with the style and organization of the existing codebase. A good patch won't be refused for stylistic reasons, but large parts of it may be rewritten and nobody wants that.
#. As you are coding, periodically merge in work from the master branch and verify you haven't broken anything by running the test suite.
#. Write documentation. Seriously.
#. Once it works, is tested, and has documentation, submit a pull request on Github.
#. Wait for it to either be merged or to receive a comment about what needs to be fixed.
#. Rejoice.

Legalese
========

To the extent that they care, contributors should keep in mind that the source of agate and therefore of any contributions are licensed under the permissive `MIT license <http://www.opensource.org/licenses/mit-license.php>`_. By submitting a patch or pull request you are agreeing to release your code under this license. You will be acknowledged in the AUTHORS file. As the owner of your specific contributions you retain the right to privately relicense your specific code contributions, however, the released version of the code can never be retracted.
