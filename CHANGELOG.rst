1.1.1
-----

* :class:`.Formula` now automatically casts computed values to specified data type unless ``invalidate`` is set to ``False``. (#398)
* Added Neil Bedi to AUTHORS.
* :meth:`.Table.rename` is implemented. (#389)
* :meth:`.TableSet.to_json` is implemented. (#374)
* :meth:`.Table.to_csv` and :meth:`.Table.to_json` will now create the target directory if it does not exist. (#392)
* :class:`.Boolean` will not correctly cast numerical ``0`` and ``1``. (#386)
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
* Migrated `csvkit <http://csvkit.readthedocs.org>`_'s unicode CSV reading/writing support into agate. (#354)

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
* Deprecated support for Python version 3.2.
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
