1.11.0 - May 27, 2024
---------------------

-  fix: The `key` argument to :meth:`.Table.to_json` errors if two values are equal, even if their CSV representation is different: for example, "1/1/2020" and "01/01/2020". However, until now, this was not the case for numbers: for example, "3.0" was treated as unequal to "3.00".

1.10.2 - April 28, 2024
-----------------------

-  fix: Version 1.10.0 errors on piped data.

1.10.1 - April 28, 2024
-----------------------

-  fix: Version 1.10.0 errors on empty tables and seeks to the file's beginning, instead of to the original offset.
-  fix: :meth:`.Number.csvify` returns a ``Decimal`` (or ``None``), instead of ``str``. :meth:`.Table.to_csv` with ``quoting=csv.QUOTE_NONNUMERIC`` now works.

1.10.0 - April 27, 2024
-----------------------

-  feat: :meth:`.Table.from_csv` reads the file line by line. If ``column_types`` is a :class:`.TypeTester`, it reads the file into memory. (#778)
-  fix: Fix :meth:`.TableSet.print_structure` for nested tablesets. (#765)

   .. code-block:: python

      import agate
      mytable = agate.Table([
          ('foo', 'FOO', 1),
          ('foo', 'FOO', 2),
          ('bar', 'BOZ', 1),
          ('bar', 'BAZ', 2),
          ('bar', 'BIZ'),
      ])

   Instead of:

   .. code-block:: none

      >>> mytable.group_by('a').group_by('b')
      AttributeError: 'TableSet' object has no attribute 'rows'

   Now:

   .. code-block:: none

      >>> mytable.group_by('a').group_by('b')
      | table   | rows |
      | ------- | ---- |
      | foo.FOO | 2    |
      | bar.BOZ | 1    |
      | bar.BAZ | 1    |
      | bar.BIZ | 1    |

1.9.1 - December 21, 2023
-------------------------

* Add Babel 2.14 support.

1.9.0 - October 17, 2023
------------------------

* feat: Add a ``text_truncation_chars`` configuration for values that exceed ``max_column_width`` in :meth:`.Table.print_table` and :meth:`.Table.print_html`.
* feat: Add a ``number_truncation_chars`` configuration for values that exceed ``max_precision`` in :meth:`.Table.print_table` and :meth:`.Table.print_html`.

1.8.0 - October 10, 2023
------------------------

* feat: Lowercase the ``null_values`` provided to individual data types, since all comparisons to ``null_values`` are case-insensitive. (#770)
* feat: :class:`.Mean` works with :class:`.TimeDelta`. (#761)
* Switch from ``pytz`` to ``ZoneInfo``.
* Add Python 3.12 support.
* Drop Python 3.7 support (end-of-life was June 27, 2023).

1.7.1 - January 4, 2023
-----------------------

* Allow parsedatetime 2.6.

1.7.0 - January 3, 2023
-----------------------

* Add Python 3.10 and 3.11 support.
* Drop support for Python 2.7 (EOL 2020-01-01), 3.6 (2021-12-23).

1.6.3 - July 15, 2021
---------------------

* feat: :meth:`.Table.from_csv` accepts a ``row_limit`` keyword argument. (#740)
* feat: :meth:`.Table.from_json` accepts an ``encoding`` keyword argument. (#734)
* feat: :meth:`.Table.print_html` accepts a ``max_precision`` keyword argument, like :meth:`.Table.print_table`. (#753)
* feat: :class:`.TypeTester` accepts a ``null_values`` keyword argument, like individual data types. (#745)
* feat: :class:`.Min`, :class:`.Max` and :class:`.Sum` (#735) work with :class:`.TimeDelta`.
* feat: :class:`.FieldSizeLimitError` includes the line number in the error message. (#681)
* feat: :class:`.csv.Sniffer` warns on error while sniffing CSV dialect.
* fix: :meth:`.Table.normalize` works with basic processing methods. (#691)
* fix: :meth:`.Table.homogenize` works with basic processing methods. (#756)
* fix: :meth:`.Table.homogenize` casts ``compare_values`` and ``default_row``. (#700)
* fix: :meth:`.Table.homogenize` accepts tuples. (#710)
* fix: :meth:`.TableSet.group_by` accepts input with no rows. (#703)
* fix: :class:`.TypeTester` warns if a column specified by the ``force`` argument is not in the table, instead of raising an error. (#747)
* fix: Aggregations return ``None`` if all values are ``None``, instead of raising an error. Note that ``Sum``, ``MaxLength`` and ``MaxPrecision`` continue to return ``0`` if all values are ``None``. (#706)
* fix: Ensure files are closed when errors occur. (#734)
* build: Make PyICU an optional dependency.
* Drop support for Python 3.4 (2019-03-18), 3.5 (2020-09-13).

1.6.2 - March 10, 2021
----------------------

* feat: :meth:`.Date.__init__` and :meth:`.DateTime.__init__` accepts a ``locale`` keyword argument (e.g. :code:`en_US`) for parsing formatted dates. (#730)
* feat: :meth:`.Number.cast` casts ``True`` to ``1`` and ``False`` to ``0``. (#733)
* fix: :meth:`.utils.max_precision` ignores infinity when calculating precision. (#726)
* fix: :meth:`.Date.cast` catches ``OverflowError`` when type testing. (#720)
* Included examples in Python package. (#716)

1.6.1 - March 11, 2018
----------------------

* feat: :meth:`.Table.to_json` can use Decimal as keys. (#696)
* fix: :meth:`.Date.cast` and :meth:`.DateTime.cast` no longer parse non-date strings that contain date sub-strings as dates. (#705)
* docs: Link to tutorial now uses version through Sphinx to avoid bad links on future releases. (#682)

1.6.0 - February 28, 2017
-------------------------

This update should not cause any breaking changes, however, it is being classified as major release because the dependency on awesome-slugify, which is licensed with GPLv3, has been replaced with python-slugify, which is licensed with MIT.

* Suppress warning from babel about Time Zone expressions on Python 3.6. (#665)
* Reimplemented slugify with python-slugify instead of awesome-slugify. (#660)
* Slugify renaming of duplicate values is now consistent with :meth:`.Table.init`. (#615)

1.5.5 - December 29, 2016
-------------------------

* Added a "full outer join" example to the SQL section of the cookbook. (#658)
* Warnings are now more explicit when column names are missing. (#652)
* :meth:`.Date.cast` will no longer parse strings like :code:`05_leslie3d_base` as dates. (#653)
* :meth:`.Text.cast` will no longer strip leading or trailing whitespace. (#654)
* Fixed :code:`'NoneType' object has no attribute 'groupdict'` error in :meth:`.TimeDelta.cast`. (#656)

1.5.4 - December 27, 2016
-------------------------

* Cleaned up handling of warnings in tests.
* Blank column names are not treated as unspecified (letter names will be generated).

1.5.3 - December 26, 2016
-------------------------

This is a minor release that adds one feature: sequential joins (by row number). It also fixes several small bugs blocking a downstream release of csvkit.

* Fixed empty :class:`.Table` column names would be intialized as list instead of tuple.
* :meth:`.Table.join` can now join by row numbers—a sequential join.
* :meth:`.Table.join` now supports full outer joins via the ``full_outer`` keyword.
* :meth:`.Table.join` can now accept column indicies instead of column names.
* :meth:`.Table.from_csv` now buffers input files to prevent issues with using STDIN as an input.

1.5.2 - December 24, 2016
-------------------------

* Improved handling of non-ascii encoded CSV files under Python 2.

1.5.1 - December 23, 2016
-------------------------

This is a minor release fixing several small bugs that were blocking a downstream release of csvkit.

* Documented differing behavior of :class:`.MaxLength` under Python 2. (#649)
* agate is now tested against Python 3.6. (#650)
* Fix bug when :class:`.MaxLength` was called on an all-null column.
* Update extensions documentation to match new API. (#645)
* Fix bug in :class:`.Change` and :class:`.PercentChange` where ``0`` values could cause ``None`` to be returned incorrectly.

1.5.0 - November 16, 2016
-------------------------

This release adds SVG charting via the `leather <https://leather.rtfd.io>`_ charting library. Charts methods have been added for both :class:`.Table` and :class:`.TableSet`. (The latter create lattice plots.) See the revised tutorial and new cookbook entries for examples. Leather is still an early library. Please `report any bugs <https://github.com/wireservice/agate/issues>`_.

Also in this release are a :class:`.Slugify` computation and a variety of small fixes and improvements.

The complete list of changes is as follows:

* Remove support for monkey-patching of extensions. (#594)
* :class:`.TableSet` methods which proxy :class:`.Table` methods now appear in the API docs. (#640)
* :class:`.Any` and :class:`.All` aggregations no longer behave differently for boolean data. (#636)
* :class:`.Any` and :class:`.All` aggregations now accept a single value as a test argument, in addition to a function.
* :class:`.Any` and :class:`.All` aggregations now require a test argument.
* Tables rendered by :meth:`.Table.print_table` are now GitHub Flavored Markdown (GFM) compatible. (#626)
* The agate tutorial has been converted to a Jupyter Notebook.
* :class:`.Table` now supports ``len`` as a proxy for ``len(table.rows)``.
* Simple SVG charting is now integrated via `leather <https://leather.rtfd.io>`_.
* Added :class:`.First` computation. (#634)
* :meth:`.Table.print_table` now has a `max_precision` argument to limit Number precision. (#544)
* Slug computation now accepts an array of column names to merge. (#617)
* Cookbook: standardize column values with :class:`.Slugify` computation. (#613)
* Cookbook: slugify/standardize row and column names. (#612)
* Fixed condition that prevents integer row names to allow bools in :meth:`.Table.__init__`. (#627)
* :class:`.PercentChange` is now null-safe, returns None for null values. (#623)
* :class:`.Table` can now be iterated, yielding :class:`Row` instances. (Previously it was necessarily to iterate :code:`table.rows`.)

1.4.0 - May 26, 2016
--------------------

This release adds several new features, fixes numerous small bug-fixes, and improves performance for common use cases. There are some minor breaking changes, but few user are likely to encounter them. The most important changes in this release are:

1. There is now a :meth:`.TableSet.having` method, which behaves similarly to SQL's ``HAVING`` keyword.

2. :meth:`.Table.from_csv` is much faster. In particular, the type inference routines for parsing numbers have been optimized.

3. The :meth:`.Table.compute` method now accepts a ``replace`` keyword which allows new columns to replace existing columns "in place."" (As with all agate operations, a new table is still created.)

4. There is now a :class:`.Slug` computation which can be used to compute a column of slugs. The :meth:`.Table.rename` method has also added new options for slugifying column and row names.

The complete list of changes is as follows:

* Added a deprecation warning for ``patch`` methods. New extensions should not use it. (#594)
* Added :class:`.Slug` computation (#466)
* Added ``slug_columns`` and ``slug_rows`` arguments to :meth:`Table.rename`. (#466)
* Added :meth:`.utils.slugify` to standardize a sequence of strings. (#466)
* :meth:`.Table.__init__` now prints row and column on ``CastError``. (#593)
* Fix null sorting in :meth:`.Table.order_by` when ordering by multiple columns. (#607)
* Implemented configuration system.
* Fixed bug in :meth:`.Table.print_bars` when ``value_column`` contains ``None`` (#608)
* :meth:`.Table.print_table` now restricts header on max_column_width. (#605)
* Cookbook: filling gaps in a dataset with Table.homogenize. (#538)
* Reduced memory usage and improved performance of :meth:`.Table.from_csv`.
* :meth:`.Table.from_csv` no longer accepts a sequence of row ids for :code:`skip_lines`.
* :meth:`.Number.cast` is now three times as fast.
* :class:`.Number` now accepts :code:`group_symbol`, :code:`decimal_symbol` and :code:`currency_symbols` arguments. (#224)
* Tutorial: clean up state data under computing columns (#570)
* :meth:`.Table.__init__` now explicitly checks that ``row_names`` are not ints. (#322)
* Cookbook: CPI deflation, agate-lookup. (#559)
* :meth:`.Table.bins` now includes values outside ``start`` or ``end`` in computed ``column_names``. (#596)
* Fixed bug in :meth:`.Table.bins` where ``start`` or ``end`` arguments were ignored when specified alone. (#599)
* :meth:`.Table.compute` now accepts a :code:`replace` argument that allows columns to be overwritten. (#597)
* :meth:`.Table.from_fixed` now creates an agate table from a fixed-width file. (#358)
* :mod:`.fixed` now implements a general-purpose fixed-width file reader. (#358)
* :class:`TypeTester` now correctly parses negative currency values as Number. (#595)
* Cookbook: removing a column (`select` and `exclude`). (#592)
* Cookbook: overriding specific column types. (#591)
* :class:`.TableSet` now has a :meth:`.TableSet._fork` method used internally for deriving new tables.
* Added an example of SQL's :code:`HAVING` to the cookbook.
* :meth:`.Table.aggregate` interface has been revised to be more similar to :meth:`.TableSet.aggregate`.
* :meth:`.TableSet.having` is now implemented. (#587)
* There is now a better error when a forced column name does not exist. (#591)
* Arguments to :meth:`.Table.print_html` now mirror :meth:`.Table.print_table`.

1.3.1 - March 30, 2016
----------------------

The major feature of this release is new API documentation. Several minor features and bug fixes are also included. There are no major breaking changes in this release.

Internally, the agate codebase has been reorganized to be more modular, but this should be invisible to most users.

* The :class:`.MaxLength` aggregation now returns a `Decimal` object. (#574)
* Fixed an edge case where datetimes were parsed as dates. (#568)
* Fixed column alignment in tutorial tables. (#572)
* :meth:`.Table.print_table` now defaults to printing ``20`` rows and ``6`` columns. (#589)
* Added Eli Murray to AUTHORS.
* :meth:`.Table.__init__` now accepts a dict to specify partial column types. (#580)
* :meth:`.Table.from_csv` now accepts a ``skip_lines`` argument. (#581)
* Moved every :class:`.Aggregation` and :class:`.Computation` into their own modules. (#565)
* :class:`.Column` and :class:`.Row` are now importable from `agate`.
* Completely reorgnized the API documentation.
* Moved unit tests into modules to match new code organization.
* Moved major :class:`.Table` and :class:`.TableSet` methods into their own modules.
* Fixed bug when using non-unicode encodings with :meth:`.Table.from_csv`. (#560)
* :meth:`.Table.homogenize` now accepts an array of values as compare values if key is a single column name. (#539)

1.3.0 - February 28, 2016
-------------------------

This version implements several new features and includes two major breaking changes.

Please take note of the following breaking changes:

1. There is no longer a :code:`Length` aggregation. The more obvious :class:`.Count` is now used instead.

2. Agate's replacements for Python's CSV reader and writer have been moved to the :code:`agate.csv` namespace. To use as a drop-in replacement: :code:`from agate import csv`.

The major new features in this release are primarly related to transforming (reshaping) tables. They are:

1. :meth:`.Table.normalize` for converting columns to rows.
2. :meth:`.Table.denormalize` for converting rows to columns.
3. :meth:`.Table.pivot` for generating "crosstabs".
4. :meth:`.Table.homogenize` for filling gaps in data series.

Please see the following complete list of changes for a variety of other bug fixes and improvements.

* Moved CSV reader/writer to :code:`agate.csv` namespace.
* Added numerous new examples to the R section of the cookbook. (#529-#535)
* Updated Excel cookbook entry for pivot tables. (#536)
* Updated Excel cookbook entry for VLOOKUP. (#537)
* Fix number rendering in :meth:`.Table.print_table` on Windows. (#528)
* Added cookbook examples of using :meth:`.Table.pivot` to count frequency/distribution.
* :meth:`.Table.bins` now has smarter output column names. (#524)
* :meth:`.Table.bins` is now a wrapper around pivot. (#522)
* :meth:`.Table.counts` has been removed. Use :meth:`.Table.pivot` instead. (#508)
* :class:`.Count` can now count non-null values in a column.
* Removed :class:`.Length`. :class:`.Count` now works without any arguments. (#520)
* :meth:`.Table.pivot` implemented. (#495)
* :meth:`.Table.denormalize` implemented. (#493)
* Added ``columns`` argument to :meth:`Table.join`. (#479)
* Cookbook: Custom statistics/agate.Summary
* Added Kevin Schaul to AUTHORS.
* :meth:`Quantiles.locate` now correctly returns `Decimal` instances. (#509)
* Cookbook: Filter for distinct values of a column (#498)
* Added :meth:`.Column.values_distinct()` (#498)
* Cookbook: Fuzzy phonetic search example. (#207)
* Cookbook: Create a table from a remote file. (#473)
* Added ``printable`` argument to :meth:`.Table.print_bars` to use only printable characters. (#500)
* :class:`.MappedSequence` now throws an explicit error on __setitem__. (#499)
* Added ``require_match`` argument to :meth:`.Table.join`. (#480)
* Cookbook: Rename columns in a table. (#469)
* :meth:`.Table.normalize` implemented. (#487)
* Added :class:`.Percent` computation with example in Cookbook. (#490)
* Added Ben Welsh to AUTHORS.
* :meth:`.Table.__init__` now throws a warning if auto-generated columns are used. (#483)
* :meth:`.Table.__init__` no longer fails on duplicate columns. Instead it renames them and throws a warning. (#484)
* :meth:`.Table.merge` now takes a ``column_names`` argument to specify columns included in new table. (#481)
* :meth:`.Table.select` now accepts a single column name as a key.
* :meth:`.Table.exclude` now accepts a single column name as a key.
* Added :meth:`.Table.homogenize` to find gaps in a table and fill them with default rows. (#407)
* :meth:`.Table.distinct` now accepts sequences of column names as a key.
* :meth:`.Table.join` now accepts sequences of column names as either a left or right key. (#475)
* :meth:`.Table.order_by` now accepts a sequence of column names as a key.
* :meth:`.Table.distinct` now accepts a sequence of column names as a key.
* :meth:`.Table.join` now accepts a sequence of column names as either a left or right key. (#475)
* Cookbook: Create a table from a DBF file. (#472)
* Cookbook: Create a table from an Excel spreadsheet.
* Added explicit error if a filename is passed to the :class:`.Table` constructor. (#438)

1.2.2 - February 5, 2016
------------------------

This release adds several minor features. The only breaking change is that default column names will now be lowercase instead of uppercase. If you depended on these names in your scripts you will need to update them accordingly.

* :class:`.TypeTester` no longer takes a ``locale`` argument. Use ``types`` instead.
* :class:`.TypeTester` now takes a ``types`` argument that is a list of possible types to test. (#461)
* Null conversion can now be disabled for :class:`.Text` by passing ``cast_nulls=False``. (#460)
* Default column names are now lowercase letters instead of uppercase. (#464)
* :meth:`.Table.merge` can now merge tables with different columns or columns in a different order. (#465)
* :meth:`.MappedSequence.get` will no longer raise ``KeyError`` if a default is not provided. (#467)
* :class:`.Number` can now test/cast the ``long`` type on Python 2.

1.2.1 - February 5, 2016
------------------------

This release implements several new features and bug fixes. There are no significant breaking changes.

Special thanks to `Neil Bedi <https://github.com/nbedi>`_ for his extensive contributions to this release.

* Added a ``max_column_width`` argument to :meth:`.Table.print_table`. Defaults to ``20``. (#442)
* :meth:`.Table.from_json` now defers most functionality to :meth:`.Table.from_object`.
* Implemented :meth:`.Table.from_object` for parsing JSON-like Python objects.
* Fixed a bug that prevented :meth:`.Table.order_by` on empty table. (#454)
* :meth:`.Table.from_json` and :meth:`TableSet.from_json` now have ``column_types`` as an optional argument. (#451)
* :class:`.csv.Reader` now has ``line_numbers`` and ``header`` options to add column for line numbers (#447)
* Renamed ``maxfieldsize`` to ``field_size_limit`` in :class:`.csv.Reader` for consistency (#447)
* :meth:`.Table.from_csv` now has a ``sniff_limit`` option to use :class:`.csv.Sniffer` (#444)
* :class:`.csv.Sniffer` implemented. (#444)
* :meth:`.Table.__init__` no longer fails on empty rows. (#445)
* :meth:`.TableSet.from_json` implemented. (#373)
* Fixed a bug that breaks :meth:`TypeTester.run` on variable row length. (#440)
* Added :meth:`.TableSet.__str__` to display :class:`.Table` keys and row counts. (#418)
* Fixed a bug that incorrectly checked for column_types equivalence in :meth:`.Table.merge` and :meth:`.TableSet.__init__`. (#435)
* :meth:`.TableSet.merge` now has the ability to specify grouping factors with ``group``, ``group_name`` and ``group_type``. (#406)
* :class:`.Table` can now be constructed with ``None`` for some column names. Those columns will receive letter names. (#432)
* Slightly changed the parsing of dates and datetimes from strings.
* Numbers are now written to CSV without extra zeros after the decimal point. (#429)
* Made it possible for ``datetime.date`` instances to be considered valid :class:`.DateTime` inputs. (#427)
* Changed preference order in type testing so :class:`.Date` is preferred to :class:`.DateTime`.
* Removed ``float_precision`` argument from :class:`.Number`. (#428)
* :class:`.AgateTestCase` is now available as ``agate.AgateTestCase``. (#426)
* :meth:`.TableSet.to_json` now has an ``indent`` option for use with ``nested``.
* :meth:`.TableSet.to_json` now has a ``nested`` option for writing a single, nested JSON file. (#417)
* :meth:`.TestCase.assertRowNames` and :meth:`.TestCase.assertColumnNames` now validate the row and column instance keys.
* Fixed a bug that prevented :meth:`.Table.rename` from renaming column names in :class:`.Row` instances. (#423)

1.2.0 - January 18, 2016
------------------------

This version introduces one breaking change, which is only relevant if you are using custom :class:`.Computation` subclasses.

1. :class:`.Computation` has been modified so that :meth:`.Computation.run` takes a :class:`.Table` instance as its argument, rather than a single row. It must return a sequence of values to use for a new column. In addition, the :meth:`.Computation._prepare` method has been renamed to :meth:`.Computation.validate` to more accurately describe it's function. These changes were made to facilitate computing moving averages, streaks and other values that require data for the full column.

* Existing :class:`.Aggregation` subclasses have been updated to use :meth:`.Aggregate.validate`. (This brings a noticeable performance boost.)
* :class:`.Aggregation` now has a :meth:`.Aggregation.validate` method that functions identically to :meth:`.Computation.validate`. (#421)
* :meth:`.Change.validate` now correctly raises :class:`.DataTypeError`.
* Added a ``SimpleMovingAverage`` implementation to the cookbook's examples of custom :class:`.Computation` classes.
* :meth:`.Computation._prepare` has been renamed to :meth:`.Computation.validate`.
* :meth:`.Computation.run` now takes a :class:`.Table` instance as an argument. (#415)
* Fix a bug in Python 2 where printing a table could raise ``decimal.InvalidOperation``. (#412)
* Fix :class:`.Rank` so it returns Decimal. (#411)
* Added Taurus Olson to AUTHORS.
* Printing a table will now print the table's structure.
* :meth:`.Table.print_structure` implemented. (#393)
* Added Geoffrey Hing to AUTHORS.
* :meth:`.Table.print_html` implemented. (#408)
* Instances of :class:`.Date` and :class:`.DateTime` can now be pickled. (#362)
* :class:`.AgateTestCase` is available as ``agate.testcase.AgateTestCase`` for extensions to use. (#384)
* :meth:`.Table.exclude` implemented. Opposite of :meth:`.Table.select`. (#388)
* :meth:`.Table.merge` now accepts a ``row_names`` argument. (#403)
* :class:`.Formula` now automatically casts computed values to specified data type unless ``cast`` is set to ``False``. (#398)
* Added Neil Bedi to AUTHORS.
* :meth:`.Table.rename` is implemented. (#389)
* :meth:`.TableSet.to_json` is implemented. (#374)
* :meth:`.Table.to_csv` and :meth:`.Table.to_json` will now create the target directory if it does not exist. (#392)
* :class:`.Boolean` will now correctly cast numerical ``0`` and ``1``. (#386)
* :meth:`.Table.merge` now consistently maps column names to rows. (#402)

1.1.0 - November 4, 2015
------------------------

This version of agate introduces three major changes.

1. :class:`.Table`, :meth:`.Table.from_csv` and :meth:`.TableSet.from_csv` now all take ``column_names`` and ``column_types`` as separate arguments instead of as a sequence of tuples. This was done to enable more flexible type inference and to streamline the API.
2. The interfaces for :meth:`.TableSet.aggregate` and :meth:`.Table.compute` have been changed. In both cases the new column name now comes first. Aggregations have also been modified so that the input column name is an argument to the aggregation class, rather than a third element in the tuple.
3. This version drops support for Python 2.6. Testing and bug-fixing for this version was taking substantial time with no evidence that anyone was actually using it. Also, multiple dependencies claim to not support 2.6, even though agate's tests were passing.

* DataType's now have :meth:`.DataType.csvify` and :meth:`.DataType.jsonify` methods for serializing native values.
* Added a dependency on `isodate <https://github.com/gweis/isodate>`_ for handling ISO8601 formatted dates. (#233)
* :class:`.Aggregation` results are no longer cached. (#378)
* Removed `Column.aggregate` method. Use :meth:`.Table.aggregate` instead. (#378)
* Added :meth:`.Table.aggregate` for aggregating single column results. (#378)
* :class:`.Aggregation` subclasses now take column names as their first argument. (#378)
* :meth:`.TableSet.aggregate` and :meth:`.Table.compute` now take the new column name as the first argument. (#378)
* Remove support for Python 2.6.
* :meth:`.Table.to_json` is implemented. (#345)
* :meth:`.Table.from_json` is implemented. (#344, #347)
* :class:`.Date` and :class:`.DateTime` type testing now takes specified format into account. (#361)
* :class:`.Number` data type now takes a ``float_precision`` argument.
* :class:`.Number` data types now work with native float values. (#370)
* :class:`.TypeTester` can now validate Python native types (not just strings). (#367)
* :class:`.TypeTester` can now be used with the :class:`.Table` constructor, not just :meth:`.Table.from_csv`. (#350)
* :class:`.Table`, :meth:`.Table.from_csv` and :meth:`.TableSet.from_csv` now take ``column_names`` and ``column_types`` as separate parameters. (#350)
* :const:`.DEFAULT_NULL_VALUES` (the list of strings that mean null) is now importable from ``agate``.
* :meth:`.Table.from_csv` and :meth:`.Table.to_csv` are now unicode-safe without separately importing csvkit.
* ``agate`` can now be used as a drop-in replacement for Python's ``csv`` module.
* Migrated `csvkit <https://csvkit.readthedocs.org>`_'s unicode CSV reading/writing support into agate. (#354)

1.0.1 - October 29, 2015
------------------------

* TypeTester now takes a "limit" arg that restricts how many rows it tests. (#332)
* Table.from_csv now supports CSVs with neither headers nor manual column names.
* Tables can now be created with automatically generated column names. (#331)
* File handles passed to Table.to_csv are now left open. (#330)
* Added Table.print_csv method. (#307, #339)
* Fixed stripping currency symbols when casting Numbers from strings. (#333)
* Fixed two major join issues. (#336)

1.0.0 - October 22, 2015
------------------------

* Table.from_csv now defaults to TypeTester() if column_info is not provided. (#324)
* New tutorial section: "Navigating table data" (#315)
* 100% test coverage reached. (#312)
* NullCalculationError is now a warning instead of an error. (#311)
* TableSet is now a subclass of MappedSequence.
* Rows and Columns are now subclasses of MappedSequence.
* Add Column.values_without_nulls_sorted().
* Column.get_data_without_nulls() is now Column.values_without_nulls().
* Column.get_data_sorted() is now Column.values_sorted().
* Column.get_data() is now Column.values().
* Columns can now be sliced.
* Columns can now be indexed by row name. (#301)
* Added support for Python 3.5.
* Row objects can now be sliced. (#303)
* Replaced RowSequence and ColumnSequence with MappedSequence.
* Replace RowDoesNotExistError with KeyError.
* Replaced ColumnDoesNotExistError with IndexError.
* Removed unnecessary custom RowIterator, ColumnIterator and CellIterator.
* Performance improvements for Table "forks". (where, limit, etc)
* TableSet keys are now converted to row names during aggregation. (#291)
* Removed fancy __repr__ implementations. Use __str__ instead. (#290)
* Rows can now be accessed by name as well as index. (#282)
* Added row_names argument to Table constructor. (#282)
* Removed Row.table and Row.index properties. (#287)
* Columns can now be accessed by index as well as name. (#281)
* Added column name and type validation to Table constructor. (#285)
* Table now supports variable-length rows during construction. (#39)
* aggregations.Summary implemented for generic aggregations. (#181)
* Fix TableSet.key_type being lost after proxying Table methods. (#278)
* Massive performance increases for joins. (#277)
* Added join benchmark. (#73)

0.11.0 - October 6, 2015
------------------------

* Implemented __repr__ for Table, TableSet, Column and Row. (#261)
* Row.index property added.
* Column constructor no longer takes a data_type argument.
* Column.index and Column.name properties added.
* Table.counts implemented. (#271)
* Table.bins implemented. (#267, #227)
* Table.join now raises ColumnDoesNotExistError. (#264)
* Table.select now raises ColumnDoesNotExistError.
* computations.ZScores moved into agate-stats.
* computations.Rank cmp argument renamed comparer.
* aggregations.MaxPrecision added. (#265)
* Table.print_bars added.
* Table.pretty_print renamed Table.print_table.
* Reimplement Table method proxying via @allow_tableset_proxy decorator. (#263)
* Add agate-stats references to docs.
* Move stdev_outliers, mad_outliers and pearson_correlation into agate-stats. (#260)
* Prevent issues with applying patches multiple times. (#258)

0.10.0 - September 22, 2015
---------------------------

* Add reverse and cmp arguments to Rank computation. (#248)
* Document how to use agate-sql to read/write SQL tables. (#238, #241)
* Document how to write extensions.
* Add monkeypatching extensibility pattern via utils.Patchable.
* Reversed order of argument pairs for Table.compute. (#249)
* TableSet.merge method can be used to ungroup data. (#253)
* Columns with identical names are now suffixed "2" after a Table.join.
* Duplicate key columns are no longer included in the result of a Table.join. (#250)
* Table.join right_key no longer necessary if identical to left_key. (#254)
* Table.inner_join is now more. Use `inner` keyword to Table.join.
* Table.left_outer_join is now Table.join.

0.9.0 - September 14, 2015
--------------------------

* Add many missing unit tests. Up to 99% coverage.
* Add property accessors for TableSet.key_name and TableSet.key_type. (#247)
* Table.rows and Table.columns are now behind properties. (#247)
* Column.data_type is now a property. (#247)
* Table[Set].get_column_types() is now the Table[Set].column_types property. (#247)
* Table[Set].get_column_names() is now the Table[Set].column_names property. (#247)
* Table.pretty_print now displays consistent decimal places for each Number column.
* Discrete data types (Number, Date etc) are now right-aligned in Table.pretty_print.
* Implement aggregation result caching. (#245)
* Reimplement Percentiles, Quartiles, etc as aggregations.
* UnsupportedAggregationError is now used to disable TableSet aggregations.
* Replaced several exceptions with more general DataTypeError.
* Column type information can now be accessed as Column.data_type.
* Eliminated Column subclasses. Restructured around DataType classes.
* Table.merge implemented. (#9)
* Cookbook: guess column types. (#230)
* Fix issue where all group keys were being cast to text. (#235)
* Table.group_by will now default key_type to the type of the grouping column. (#234)
* Add Matt Riggott to AUTHORS. (#231)
* Support file-like objects in Table.to_csv and Table.from_csv. (#229)
* Fix bug when applying multiple computations with Table.compute.

0.8.0 - September 9, 2015
-------------------------

* Cookbook: dealing with locales. (#220)
* Cookbook: working with dates and times.
* Add timezone support to DateTimeType.
* Use pytimeparse instead of python-dateutil. (#221)
* Handle percents and currency symbols when casting numbers. (#217)
* Table.format is now Table.pretty_print. (#223)
* Rename TextType to Text, NumberType to Number, etc.
* Rename agate.ColumnType to agate.DataType (#216)
* Rename agate.column_types to agate.data_types.
* Implement locale support for number parsing. (#116)
* Cookbook: ranking. (#110)
* Cookbook: date change and date ranking. (#113)
* Add tests for unicode support. (#138)
* Fix computations.ZScores calculation. (#123)
* Differentiate sample and population variance and stdev. (#208)
* Support for overriding column inference with "force".
* Competition ranking implemented as default. (#125)
* TypeTester: robust type inference. (#210)

0.7.0 - September 3, 2015
-------------------------

* Cookbook: USA Today diversity index.
* Cookbook: filter to top x%. (#47)
* Cookbook: fuzzy string search example. (#176)
* Values to coerce to true/false can now be overridden for BooleanType.
* Values to coerce to null can now be overridden for all ColumnType subclasses. (#206)
* Add key_type argument to TableSet and Table.group_by. (#205)
* Nested TableSet's and multi-dimensional aggregates. (#204)
* TableSet.aggregate will now use key_name as the group column name. (#203)
* Added key_name argument to TableSet and Table.group_by.
* Added Length aggregation and removed count from TableSet.aggregate output. (#203)
* Fix error messages for RowDoesNotExistError and ColumnDoesNotExistError.

0.6.0 - September 1, 2015
-------------------------

* Fix missing package definition in setup.py.
* Split Analysis off into the proof library.
* Change computation now works with DateType, DateTimeType and TimeDeltaType. (#159)
* TimeDeltaType and TimeDeltaColumn implemented.
* NonNullAggregation class removed.
* Some private Column methods made public. (#183)
* Rename agate.aggegators to agate.aggregations.
* TableSet.to_csv implemented. (#195)
* TableSet.from_csv implemented. (#194)
* Table.to_csv implemented (#169)
* Table.from_csv implemented. (#168)
* Added Table.format method for pretty-printing tables. (#191)
* Analysis class now implements a caching workflow. (#171)

0.5.0 - August 28, 2015
-----------------------

* Table now takes (column_name, column_type) pairs. (#180)
* Renamed the library to agate. (#179)
* Results of common column operations are now cached using a common memoize decorator. (#162)
* ated support for Python version 3.2.
* Added support for Python wheel packaging. (#127)
* Add PercentileRank computation and usage example to cookbook. (#152)
* Add indexed change example to cookbook. (#151)
* Add annual change example to cookbook. (#150)
* Column.aggregate now invokes Aggregations.
* Column.any, NumberColumn.sum, etc. converted to Aggregations.
* Implement Aggregation and subclasses. (#155)
* Move ColumnType subclasses and ColumnOperation subclasses into new modules.
* Table.percent_change, Table.rank and Table.zscores reimplemented as Computers.
* Computer implemented. Table.compute reimplemented. (#147)
* NumberColumn.iqr (inter-quartile range) implemented. (#102)
* Remove Column.counts as it is not the best way.
* Implement ColumnOperation and subclasses.
* Table.aggregate migrated to TableSet.aggregate.
* Table.group_by now supports grouping by a key function. (#140)
* NumberColumn.deciles implemented.
* NumberColumn.quintiles implemented. (#46)
* NumberColumn.quartiles implemented. (#45)
* Added robust test case for NumberColumn.percentiles. (#129)
* NumberColumn.percentiles reimplemented using new method. (#130)
* Reorganized and modularized column implementations.
* Table.group_by now returns a TableSet.
* Implement TableSet object. (#141)

0.4.0 - September 27, 2014
--------------------------

* Upgrade to python-dateutil 2.2. (#134)
* Wrote introductory tutorial. (#133)
* Reorganize documentation (#132)
* Add John Heasly to AUTHORS.
* Implement percentile. (#35)
* no_null_computations now accepts args. (#122)
* Table.z_scores implemented. (#123)
* DateTimeColumn implemented. (#23)
* Column.counts now returns dict instead of Table. (#109)
* ColumnType.create_column renamed _create_column. (#118)
* Added Mick O'Brien to AUTHORS. (#121)
* Pearson correlation implemented. (#103)

0.3.0
-----

* DateType.date_format implemented. (#112)
* Create ColumnType classes to simplify data parsing.
* DateColumn implemented. (#7)
* Cookbook: Excel pivot tables. (#41)
* Cookbook: statistics, including outlier detection. (#82)
* Cookbook: emulating Underscore's any and all. (#107)
* Parameter documention for method parameters. (#108)
* Table.rank now accepts a column name or key function.
* Optionally use cdecimal for improved performance. (#106)
* Smart naming of aggregate columns.
* Duplicate columns names are now an error. (#92)
* BooleanColumn implemented. (#6)
* TextColumn.max_length implemented. (#95)
* Table.find implemented. (#14)
* Better error handling in Table.__init__. (#38)
* Collapse IntColumn and FloatColumn into NumberColumn. (#64)
* Table.mad_outliers implemented. (#93)
* Column.mad implemented. (#93)
* Table.stdev_outliers implemented. (#86)
* Table.group_by implemented. (#3)
* Cookbook: emulating R. (#81)
* Table.left_outer_join now accepts column names or key functions. (#80)
* Table.inner_join now accepts column names or key functions. (#80)
* Table.distinct now accepts a column name or key function. (#80)
* Table.order_by now accepts a column name or key function. (#80)
* Table.rank implemented. (#15)
* Reached 100% test coverage. (#76)
* Tests for Column._cast methods. (#20)
* Table.distinct implemented. (#83)
* Use assertSequenceEqual in tests. (#84)
* Docs: features section. (#87)
* Cookbook: emulating SQL. (#79)
* Table.left_outer_join implemented. (#11)
* Table.inner_join implemented. (#11)

0.2.0
-----

* Python 3.2, 3.3 and 3.4 support. (#52)
* Documented supported platforms.
* Cookbook: csvkit. (#36)
* Cookbook: glob syntax. (#28)
* Cookbook: filter to values in range. (#30)
* RowDoesNotExistError implemented. (#70)
* ColumnDoesNotExistError implemented. (#71)
* Cookbook: percent change. (#67)
* Cookbook: sampleing. (#59)
* Cookbook: random sort order. (#68)
* Eliminate Table.get_data.
* Use tuples everywhere. (#66)
* Fixes for Python 2.6 compatibility. (#53)
* Cookbook: multi-column sorting. (#13)
* Cookbook: simple sorting.
* Destructive Table ops now deepcopy row data. (#63)
* Non-destructive Table ops now share row data. (#63)
* Table.sort_by now accepts a function. (#65)
* Cookbook: pygal.
* Cookbook: Matplotlib.
* Cookbook: VLOOKUP. (#40)
* Cookbook: Excel formulas. (#44)
* Cookbook: Rounding to two decimal places. (#49)
* Better repr for Column and Row. (#56)
* Cookbook: Filter by regex. (#27)
* Cookbook: Underscore filter & reject. (#57)
* Table.limit implemented. (#58)
* Cookbook: writing a CSV. (#51)
* Kill Table.filter and Table.reject. (#55)
* Column.map removed. (#43)
* Column instance & data caching implemented. (#42)
* Table.select implemented. (#32)
* Eliminate repeated column index lookups. (#25)
* Precise DecimalColumn tests.
* Use Decimal type everywhere internally.
* FloatColumn converted to DecimalColumn. (#17)
* Added Eric Sagara to AUTHORS. (#48)
* NumberColumn.variance implemented. (#1)
* Cookbook: loading a CSV. (#37)
* Table.percent_change implemented. (#16)
* Table.compute implemented. (#31)
* Table.filter and Table.reject now take funcs. (#24)
* Column.count implemented. (#12)
* Column.counts implemented. (#8)
* Column.all implemented. (#5)
* Column.any implemented. (#4)
* Added Jeff Larson to AUTHORS. (#18)
* NumberColumn.mode implmented. (#18)

0.1.0
-----

* Initial prototype
