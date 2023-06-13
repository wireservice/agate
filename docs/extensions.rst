==========
Extensions
==========

The core agate library is designed rely on as few dependencies as possible. However, in the real world you're often going to want to interface with more specialized tools, or with other formats, such as SQL or Excel.

Using extensions
================

agate support's plugin-style extensions using a monkey-patching pattern. Libraries can be created that add new methods onto :class:`.Table` and :class:`.TableSet`. For example, `agate-sql <https://agate-sql.rtfd.org/>`_ adds the ability to read and write tables from a SQL database:

.. code-block:: python

    import agate
    import agatesql

    # After calling patch the from_sql and to_sql methods are now part of the Table class
    table = agate.Table.from_sql('postgresql:///database', 'input_table')
    table.to_sql('postgresql:///database', 'output_table')

List of extensions
==================

Here is a list of agate extensions that are known to be actively maintained:

* `agate-sql <https://agate-sql.rtfd.org/>`_: Read and write tables in SQL databases
* `agate-stats <https://agate-stats.rtfd.org/>`_: Additional statistical methods
* `agate-excel <https://agate-excel.rtfd.org/>`_: Read excel tables (xls and xlsx)
* `agate-dbf <https://agate-dbf.rtfd.org/>`_: Read dbf tables (from shapefiles)
* `agate-remote <https://agate-remote.rtfd.org/>`_: Read from remote files
* `agate-lookup <https://agate-lookup.rtfd.org/>`_: Instantly join to hosted `lookup <https://github.com/wireservice/lookup>`_ tables.

Writing your own extensions
===========================

Writing your own extensions is straightforward. Create a function that acts as your "patch" and then dynamically add it to :class:`.Table` or :class:`.TableSet`.

.. code-block:: python

    import agate

    def new_method(self):
        print('I do something to a Table when you call me.')

    agate.Table.new_method = new_method

You can also create new classmethods:

.. code-block:: python

    def new_class_method(cls):
        print('I make Tables when you call me.')

    agate.Table.new_method = classmethod(new_method)

These methods can now be called on :class:`.Table` class in your code:

.. code-block:: python

    >>> import agate
    >>> import myextension
    >>> table = agate.Table(rows, column_names, column_types)
    >>> table.new_method()
    'I do something to a Table when you call me.'
    >>> agate.Table.new_class_method()
    'I make Tables when you call me.'

The same pattern also works for adding methods to :class:`.TableSet`.
