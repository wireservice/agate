========
Tutorial
========

About this tutorial
===================

The best way to learn to use any tool is to actually use it. In this tutorial we will use agate to answer some basic questions about a dataset.

The data will be using is a copy of the `National Registery of Exonerations <http://www.law.umich.edu/special/exoneration/Pages/detaillist.aspx>`_ made on August 28th, 2015. This dataset lists individuals who are known to have been exonerated after having been wrongly convicted in United States courts. At the time the data was exported there were 1,651 entries in the registry.

Installing agate
================

Installing agate is easy::

    pip install agate

.. note::

    You should be installing agate inside a `virtualenv <http://virtualenv.readthedocs.org/en/latest/>`_. If for some crazy reason you aren't using virtualenv you will need to add a ``sudo`` to the previous command.

Getting the data
================

Let's start by creating a clean workspace::

    mkdir agate_tutorial
    cd agate_tutorial

Now let's download the data::

    curl -L -O https://github.com/onyxfish/agate/raw/master/examples/realdata/exonerations-20150828.csv

You will now have a file named ``exonerations-20150828.csv`` in your ``agate_tutorial`` directory.

Getting setup
=============

Launch the Python interpreter::

    python

Now let's import our dependencies:

.. code-block:: python

    import agate

Loading data from a CSV
=======================

The :class:`.Table` is the basic class in agate. To create a table from a CSV we use :meth:`.Table.from_csv`:

.. code-block:: python

    exonerations = agate.Table.from_csv('exonerations-20150828.csv')

With no other arguments specified, agate will automatically create an instance of :class:`.TypeTester` and use it to figure out the type of each column. TypeTester is a "best guess" approach to determining the kinds of data in your table. It can guess wrong. In that case you can create a TypeTester manually and use the ``force`` argument to override its guess for a specific column:

.. code-block:: python

    tester = agate.TypeTester(force={
        'false_evidence': agate.Boolean()
    })

    exonerations = agate.Table.from_csv('exonerations-20150828.csv', column_types=tester)`

If you already know the types of your data you may wish to skip the TypeTester entirely. You may pass sequences of column names and column types to :meth:`.Table.from_csv` as the ``column_names`` and ``column_types`` arguments, respectively.

For larger datasets the :class:`.TypeTester` can be slow to evaluate the data. In that case you can specify a `limit` argument to restrict the amount of data it will use to infer types:

.. code-block:: python

    tester = agate.TypeTester(limit=100)

    exonerations = agate.Table.from_csv('exonerations-20150828.csv', tester)

The dataset we are using in this tutorial is simple enough that we can rely on the built-in TypeTester to guess quickly and accurately.

.. note::

    agate's builtin CSV :func:`.csv_py3.reader` and :func:`.csv_py3.writer` support unicode and other encodings for both Python 2 and Python 3.

.. note::

    agate also has :meth:`.Table.from_json` for creating tables from JSON data.

Describing the table
====================

If you're working with new data, or you just need a refresher, you may want to review what columns are in the table. You can do this with the :meth:`.Table.print_structure` method or by just calling :func:`print` on the table:

.. code-block:: python

    print(exonerations)

::

    |----------------------+---------------|
    |  column_names        | column_types  |
    |----------------------+---------------|
    |  last_name           | Text          |
    |  first_name          | Text          |
    |  age                 | Number        |
    |  race                | Text          |
    |  state               | Text          |
    |  tags                | Text          |
    |  crime               | Text          |
    |  sentence            | Text          |
    |  convicted           | Number        |
    |  exonerated          | Number        |
    |  dna                 | Boolean       |
    |  dna_essential       | Text          |
    |  mistake_witness     | Boolean       |
    |  false_confession    | Boolean       |
    |  perjury             | Boolean       |
    |  false_evidence      | Boolean       |
    |  official_misconduct | Boolean       |
    |  inadequate_defense  | Boolean       |
    |----------------------+---------------|

Navigating table data
=====================

agate goes to great pains to make accessing the data in your tables work seamlessly for a wide variety of use-cases. Access by both :class:`.Column` and :class:`.Row` is supported, via the :attr:`.Table.columns` and :attr:`.Table.rows` attributes respectively.

All four of these objects are examples of :class:`.MappedSequence`, the foundational type that underlies much of agate's functionality. A MappedSequence functions very similar to a standard Python :class:`dict`, with a few important exceptions:

* Data may be accessed either by numeric index (e.g. column number) or by a non-integer key (e.g. column name).
* Items are ordered, just like an instance of :class:`collections.OrderedDict`.
* Iterating over the sequence returns its *values*, rather than its *keys*.

To demonstrate the first point, these two lines are both valid ways of getting the first column in the :code:`exonerations` table:

.. code-block:: python

    exonerations.columns['last_name']
    exonerations.columns[0]

In the same way, rows can be accessed either by numeric index or by an optional, unique "row name" specified when the table is created. In this tutorial we won't use row names, but here is an example of how they work:

.. code-block:: python

    exonerations = agate.Table.from_csv('exonerations-20150828.csv', columns, row_names=lambda r: '%(last_name)s, %(first_name)s' % (r))

    exonerations.rows[0]
    exonerations.rows['Abbitt, Joseph Lamont']

In this case we create our row names using a :keyword:`lambda` function that takes a row and returns an unique identifer. If your data has a unique column, you can also just pass the column name. (For example, a column of USPS abbrevations or FIPS codes.) Note, however, that your row names can never be :class:`int`, because that is reserved for indexing by numeric order. (A :class:`decimal.Decimal` or stringified integer is just fine.)

Once you've got a specific row, you can then access its individual values (cells, in spreadsheet-speak) either by numeric index or column name:

.. code-block:: python

    row = exonerations.rows[0]

    row[0]
    row['last_name']

And the same goes for columns, which can be indexed numerically or by row name (if one has been setup):

.. code-block:: python

    column = exonerations.columns['crime']

    column[0]
    column['Abbitt, Joseph Lamont']

For any instance of :class:`.MappedSequence`, iteration returns values, *in order*:

.. code-block:: python

    for row in exonerations.rows:
        print(row['last_name'])

::

    Abbitt
    Abdal
    Abernathy
    Acero
    Adams
    ...

To summarize, the four most common data structures in agate (:class:`.Column`, :class:`.Row`, :attr:`.Table.columns` and :attr:`.Table.rows`) are all instances of :class:`.MappedSequence` and therefore all behave in a uniform way. This is also true of :class:`.TableSet`, which will discuss later on.

Aggregating column data
=======================

With the basics out of the way, let's do some actual analysis. Analysis begins with questions, so let's ask some.

Q: **How many exonerations involved a false confession?**

Answering this question involves counting the number of ``True`` values in the ``false_confession`` column. When we created the table we specified that the data in this column contained :class:`.Boolean` data. Because of this, agate has taken care of coercing the original text data from the CSV into Python's ``True`` and ``False`` values.

We'll answer the question using an instance of :class:`.Count` which is a type of :class:`.Aggregation`. Aggregations are used to perform "column-wise" calculations. That is, they derive a new single value from the contents of a column. The :class:`.Count` aggregation can count either all values in a column, or how many times a particular value appears.

An Aggregation is applied to a table using :meth:`.Table.aggregate`.

It sounds complicated, but it's really simple. Putting it all together looks like this:

.. code-block:: python

    num_false_confessions = exonerations.aggregate(agate.Count('false_confession', True))

    print(num_false_confessions)

::

    211

Let's look at another example, this time using a numerical aggregation.

Q: **What was the median age of exonerated indviduals at time of arrest?**

.. code-block:: python

    median_age = exonerations.aggregate(agate.Median('age'))

    print(median_age)

Answer:

::

    /Users/onyxfish/src/agate/agate/warns.py:17: NullCalculationWarning: Column "age" contains nulls. These will be excluded from Median calculation.
      ), NullCalculationWarning)
    /Users/onyxfish/src/agate/agate/warns.py:17: NullCalculationWarning: Column "age" contains nulls. These will be excluded from Percentiles calculation.
      ), NullCalculationWarning)
    26

The answer to our question is "26 years old", however, as the warnings indicate, not every exonerated individual in the data has a value for the ``age`` column. The :class:`.Median` statistical operation has no standard way of accounting for null values, so it removes them before running the calculation.

Q: **How many individuals do not have an age specified in the data?**

Now that we know there are null values in the ``age`` column, we might worry about our sample size. What if most of the rows don't have an age?

.. code-block:: python

    num_without_age = exonerations.aggregate(agate.Count('age', None))

    print(num_without_age)

Answer:

::

    9

Only nine rows in this dataset don't have age, so it's certainly still useful to compute a median. However, we might still want to filter those rows out so we could have a consistent sample for all of our calculations. In the next section you'll learn how to do just that.

Different :mod:`.aggregations` can be applied depending on the type of data in each column. If none of the provided aggregations suit your needs you can use :class:`.Summary` to apply an arbitrary function to a column. If that still doesn't suit your needs you can always create your own aggregation from scratch by subclassing :class:`.Aggregation`.

Selecting and filtering data
============================

So what if those rows with no age were going to flummox our analysis? Agate's :class:`.Table` class provides a full suite of SQL-like operations including :meth:`.Table.select` for grabbing specific columns, :meth:`.Table.where` for selecting particular rows and :meth:`.Table.group_by` for grouping rows by common values.

Let's use :meth:`.Table.where` to filter our exonerations table to only those individuals that have an age specified.

.. code-block:: python

    with_age = exonerations.where(lambda row: row['age'] is not None)

You'll notice we provide a :keyword:`lambda` function to the :meth:`.Table.where`. This function is applied to each row and if it returns ``True``, then the row is included in the output table.

A crucial thing to understand about these table methods is that they return **new tables**. In our example above ``exonerations`` was a :class:`.Table` instance and we applied :meth:`.Table.where`, so ``with_age`` is a new, different :class:`Table`. The tables themselves can't be changed. You can create new tables with these methods, but you can't modify them in-place. (If this seems weird, just trust me. There are lots of good computer science-y reasons to do it this way.)

We can verify this did what we expected by counting the rows in the original table and rows in the new table:

.. code-block:: python

    old = len(exonerations.rows)
    new = len(with_age.rows)

    print(old - new)

::

    9

Nine rows were removed, which is the number of nulls we had already identified were in the column.

Now if we calculate the median age of these individuals, we don't see the warning anymore.

.. code-block:: python

    median_age = with_age.aggregate(agate.Median('age'))

    print(median_age)

::

    26

Computing new columns
=====================

In addition to "column-wise" :mod:`.aggregations` there are also "row-wise" :mod:`.computations`. Computations go through a :class:`.Table` row-by-row and derive a new column using the existing data. To perform row computations in agate we use subclasses of :class:`.Computation`.

When one or more instances of :class:`.Computation` are applied with the :meth:`.Table.compute` method, a new table is created with additional columns.

Q: **How long did individuals remain in prison before being exonerated?**

To answer this question we will apply the :class:`.Change` computation to the ``convicted`` and ``exonerated`` columns. Each of these columns contains the individual's age at the time of that event. All that :class:`.Change` does is compute the difference between two numbers. (In this case each of these columns contain a :class:`.Number`, but this will also work with :class:`.Date` or :class:`.DateTime`)

.. code-block:: python

    with_years_in_prison = exonerations.compute([
        ('years_in_prison', agate.Change('convicted', 'exonerated'))
    ])

    median_years = with_years_in_prison.aggregate(agate.Median('years_in_prison'))

    print(median_years)

::

    8

The median number of years an exonerated individual spent in prison was 8 years.

Sometimes, the built-in computations, such as :class:`.Change` won't suffice. I mentioned before that you could perform arbitrary column-wise aggregations using :class:`.Summary`. You can do the same thing for row-wise computations using :class:`.Formula`. This is somewhat analogous to Excel's cell formulas.

For example, this code will create a ``full_name`` column from the ``first_name`` and ``last_name`` columns in the data:

.. code-block:: python

    full_names = exonerations.compute([
        ('full_name', agate.Formula(agate.Text(), lambda row: '%(first_name)s %(last_name)s' % row))
    ])

For efficiency's sake, agate allows you to perform several computations at once (though they can't depend on one another):

.. code-block:: python

    with_computations = exonerations.compute([
        ('full_name', agate.Formula(agate.Text(), lambda row: '%(first_name)s %(last_name)s' % row)),
        ('years_in_prison', agate.Change('convicted', 'exonerated'))
    ])

If :class:`.Formula` is not flexible enough (for instance, if you needed to compute a new value based on the distribution of data in a column) you can always implement your own subclass of :class:`.Computation`. See the API documentation for :mod:`.computations` to see all of the supported ways to compute new data.

Sorting and slicing
===================

Q: **Who are the ten exonerated individuals who were youngest at the time they were arrested?**

Remembering that methods of tables return tables, we will use :meth:`.Table.order_by` to sort our table:

.. code-block:: python

    sorted_by_age = exonerations.order_by('age')

We can then use :meth:`.Table.limit` get only the first ten rows of the data.

.. code-block:: python

    youngest_ten = sorted_by_age.limit(10)

Now let's use :meth:`.Table.print_table` to help us pretty the results in a way we can easily review:

.. code-block:: python

    youngest_ten.print_table(max_columns=7)

::

    |------------+------------+-----+-----------+-------+---------+---------+------|
    |  last_name | first_name | age | race      | state | tags    | crime   | ...  |
    |------------+------------+-----+-----------+-------+---------+---------+------|
    |  Murray    | Lacresha   | 11  | Black     | TX    | CV, F   | Murder  | ...  |
    |  Adams     | Johnathan  | 12  | Caucasian | GA    | CV, P   | Murder  | ...  |
    |  Harris    | Anthony    | 12  | Black     | OH    | CV      | Murder  | ...  |
    |  Edmonds   | Tyler      | 13  | Caucasian | MS    |         | Murder  | ...  |
    |  Handley   | Zachary    | 13  | Caucasian | PA    | A, CV   | Arson   | ...  |
    |  Jimenez   | Thaddeus   | 13  | Hispanic  | IL    |         | Murder  | ...  |
    |  Pacek     | Jerry      | 13  | Caucasian | PA    |         | Murder  | ...  |
    |  Barr      | Jonathan   | 14  | Black     | IL    | CDC, CV | Murder  | ...  |
    |  Brim      | Dominique  | 14  | Black     | MI    | F       | Assault | ...  |
    |  Brown     | Timothy    | 14  | Black     | FL    |         | Murder  | ...  |
    |------------+------------+-----+-----------+-------+---------+---------+------|

If you find it impossible to believe that an eleven year-old was convicted of murder, I encourage you to read the Registry's `description of the case <http://www.law.umich.edu/special/exoneration/Pages/casedetail.aspx?caseid=3499>`_.

.. note::

    In the previous example we could have omitted the :meth:`.Table.limit` and passed a ``max_rows=10`` to :meth:`.Table.print_table` instead. In this case they accomplish exactly the same goal.

What if we were more curious about the *distribution* of ages, rather than the highest or lowest? agate includes the :meth:`.Table.pivot` and :meth:`.Table.bins` methods for counting values individually or by ranges. Let's try binning the ages. Then, instead of using :meth:`.Table.print_table`, we'll use :meth:`.Table.print_bars` to generate a simple, text bar chart.

.. code-block:: python

    binned_ages = exonerations.bins('age', 10, 0, 100)
    binned_ages.print_bars('age', 'Count', width=80)

::

    group      Count
    [0 - 10)       0 ▓
    [10 - 20)    307 ▓░░░░░░░░░░░░░░░░░░░░░░░░
    [20 - 30)    718 ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    [30 - 40)    377 ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    [40 - 50)    176 ▓░░░░░░░░░░░░░░
    [50 - 60)     53 ▓░░░░
    [60 - 70)     10 ▓░
    [70 - 80)      0 ▓
    [80 - 90)      1 ▓
    [90 - 100]     0 ▓
    None           9 ▓░
                     +---------------+--------------+--------------+---------------+
                     0              200            400            600            800

Notice that we specify we want :code:`10` bins spanning the range :code:`0` to :code:`100`. If these values are omitted agate will attempt to infer good defaults. We also specify that we want our bar chart to span a width of :code:`80` characters. This can be adjusted to a suitable width for your terminal or document.

.. note::

    If you use a monospaced font, such as Courier, you can copy and paste agate bar charts into emails or documents. No screenshots required.

Grouping and aggregating
========================

Q: **Which state has seen the most exonerations?**

This question can't be answered by operating on a single column. What we need is the equivalent of SQL's ``GROUP BY``. agate supports a full set of SQL-like operations on tables. Unlike SQL, agate breaks grouping and aggregation into two discrete steps.

First, we use :meth:`.Table.group_by` to group the data by state.

.. code-block:: python

    by_state = exonerations.group_by('state')

This takes our original :class:`.Table` and groups it into a :class:`.TableSet`, which contains one table per county. As mentioned much earlier in this tutorial, TableSets are instances of :class:`.MappedSequence`. That means they work very much like :class:`.Column` and :class:`.Row`.

Now we need to aggregate the total for each state. This works in a very similar way to how it did when we were aggregating columns of a single table, except that we'll use the :class:`.Count` aggregation to count the total number of rows in each group.

.. code-block:: python

    state_totals = by_state.aggregate([
        ('count', agate.Count())
    ])

    sorted_totals = state_totals.order_by('count', reverse=True)

    sorted_totals.print_table(max_rows=5)

::

    |--------+--------|
    |  state | count  |
    |--------+--------|
    |  TX    | 212    |
    |  NY    | 202    |
    |  CA    | 154    |
    |  IL    | 153    |
    |  MI    | 60     |
    |  ...   | ...    |
    |--------+--------|

You'll notice we pass a sequence of tuples to :meth:`.TableSet.aggregate`. Each one includes two elements. The first is the new column name being created. The second is an instance of some :class:`.Aggregation`. Unsurpringly, in this case the results appear to be roughly proportional to population.

Q: **What state has the longest median time in prison prior to exoneration?**

This is a much more complicated question that's going to pull together a lot of the features we've been using. We'll repeat the computations we applied before, but this time we're going to roll those computations up in state-by-state groups and then take the :class:`.Median` of each group. Then we'll sort the data and see where people have been stuck in prison the longest.

.. code-block:: python

    with_years_in_prison = exonerations.compute([
        ('years_in_prison', agate.Change('convicted', 'exonerated'))
    ])

    state_totals = with_years_in_prison.group_by('state')

    medians = state_totals.aggregate([
        ('count', agate.Count()),
        ('median_years_in_prison', agate.Median('years_in_prison'))
    ])

    sorted_medians = medians.order_by('median_years_in_prison', reverse=True)

    sorted_medians.print_table(max_rows=5)

::

    |--------+-------+-------------------------|
    |  state | count | median_years_in_prison  |
    |--------+-------+-------------------------|
    |  DC    | 15    | 27                      |
    |  NE    | 9     | 20                      |
    |  ID    | 2     | 19                      |
    |  VT    | 1     | 18                      |
    |  LA    | 45    | 16                      |
    |  ...   | ...   | ...                     |
    |--------+-------+-------------------------|

DC? Nebraska? What accounts for these states having the longest times in prison before exoneration? I have no idea! Given that the group sizes are small, it would probably be wise to look for outliers.

As with :meth:`.Table.aggregate` and :meth:`.Table.compute`, the :meth:`.TableSet.aggregate` method takes a list of aggregations to perform. You can aggregate as many columns as you like in a single step and they will all appear in the output table.

Multi-dimensional aggregation
=============================

Before we wrap up, let's try one more thing. I've already shown you that you can use :class:`.TableSet` to group instances of :class:`.Table`. However, you can also use a :class:`.TableSet` to group *other TableSets*. To put that another way, instances of :class:`.TableSet` can be *nested*.

The key to nesting data in this way is to use :meth:`.TableSet.group_by`. Before we used :meth:`.Table.group_by` to split data up into a group of tables. Now we'll use :meth:`.TableSet.group_by` to further subdivide that data. Let's look at a concrete example.

Q: **Is there a collective relationship between race, age and time spent in prison prior to exoneration?**

I'm not going to explain every stage of this analysis as most of it repeats patterns used previously. The key part to look for is the two separate uses of ``group_by``:

.. code-block:: python

    # Filters rows without age data
    only_with_age = with_years_in_prison.where(
        lambda r: r['age'] is not None
    )

    # Group by race
    race_groups = only_with_age.group_by('race')

    # Sub-group by age cohorts (20s, 30s, etc.)
    race_and_age_groups = race_groups.group_by(
        lambda r: '%i0s' % (r['age'] // 10),
        key_name='age_group'
    )

    # Aggregate medians for each group
    medians = race_and_age_groups.aggregate([
        ('count', agate.Count()),
        ('median_years_in_prison', agate.Median('years_in_prison'))
    ])

    # Sort the results
    sorted_groups = medians.order_by('median_years_in_prison', reverse=True)

    # Print out the results
    sorted_groups.print_table(max_rows=10)

::

    |------------------+-----------+-------+-------------------------|
    |  race            | age_group | count | median_years_in_prison  |
    |------------------+-----------+-------+-------------------------|
    |  Native American | 20s       | 2     | 21.5                    |
    |                  | 20s       | 1     | 19                      |
    |  Native American | 10s       | 2     | 15                      |
    |  Native American | 30s       | 2     | 14.5                    |
    |  Black           | 10s       | 188   | 14                      |
    |  Black           | 20s       | 358   | 13                      |
    |  Asian           | 20s       | 4     | 12                      |
    |  Black           | 30s       | 156   | 10                      |
    |  Caucasian       | 10s       | 76    | 8                       |
    |  Caucasian       | 20s       | 255   | 8                       |
    |  ...             | ...       | ...   | ...                     |
    |------------------+-----------+-------+-------------------------|

That's it--you made it through the tutorial! Now it's your turn!

Where to go next
================

This tutorial only scratches the surface of agate's features. For many more ideas on how to apply agate, check out the :doc:`cookbook`, which includes dozens of examples of specific features of agate as well as recipes for substituting agate for Excel, SQL, R and more. Also check out the agate's :doc:`extensions` which add support for reading/writing SQL tables, performing statistical analysis and more.

Also, if you're going to be doing data processing in Python you really ought to check out `proof <http://proof.readthedocs.org/en/latest/>`_, a library for building data processing pipelines that are repeatable and self-documenting. It will make your code cleaner and save you tons of time.

Good luck in your reporting!
