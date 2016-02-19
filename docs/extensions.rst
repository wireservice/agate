==========
Extensions
==========

agate's core featureset is designed rely on as few dependencies as possible. However, in the real world you're often going to want to interface agate with SQL, numpy or other data processing tools.

How extensions work
===================

In order to support these use-cases, but not make things excessively complicated, agate support's a simple extensibility pattern based on `monkey patching <https://en.wikipedia.org/wiki/Monkey_patch>`_. Libraries can be created that patch new methods onto :class:`.Table` and :class:`.TableSet`. For example, `agate-sql <http://agate-sql.rtfd.org/>`_ adds the ability to read and write tables from a SQL database:

.. code-block:: python

    import agate
    import agatesql

    agatesql.patch()

    # After calling patch the from_sql and to_sql methods are now part of the Table class
    table = agate.Table.from_sql('postgresql:///database', 'input_table')
    table.to_sql('postgresql:///database', 'output_table')

List of extensions
==================

Here is a list of actively supported agate extensions:

* `agate-sql <http://agate-sql.rtfd.org/>`_: Read and write tables in SQL databases
* `agate-stats <http://agate-stats.rtfd.org/>`_: Additional statistical methods
* `agate-excel <http://agate-excel.rtfd.org/>`_: Read excel tables (xls and xlsx)
* `agate-dbf <http://agate-dbf.rtfd.org/>`_: Read dbf tables (from shapefiles)
* `agate-remote <http://agate-remote.rtfd.org/>`_: Read from remote files

Writing your own extensions
===========================

Writing your own extensions is straightforward. Create a class that acts as your "patch" and when you call :meth:`. Table.monkeypatch` it will dynamically be added as a base class of :class:`.Table`.

.. code-block:: python

    import agate

    class ExamplePatch(object):
        def new_method(self):
            print('I do something to a Table when you call me.')

Then create a function that applies your patch:

.. code-block:: python

    def patch()
        agate.Table.monkeypatch(ExamplePatch)

The :class:`.Table` class will now have all the methods of :code:`ExamplePatch` as though they were defined as part of it.

.. code-block:: python

    >>> import agate
    >>> import myextension
    >>> myextension.patch()
    >>> table = agate.Table(rows, column_names, column_types)
    >>> table.new_method()
    'I do something to a Table when you call me.'

The same pattern also works for adding methods to :class:`.TableSet`.

.. warning::

    Extensions are added as **base classes** of :class:`.Table` so you can not use them to override the implementation of an existing method. They are perfect for adding features, but if you need to actually modify how agate works, then you'll need to use a subclass. Any shadowed method will be ignored.
