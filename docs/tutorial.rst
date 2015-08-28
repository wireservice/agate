========
Tutorial
========

About this tutorial
===================

The best way to learn to use any tool is to actually use it. In this tutorial we will answer some basic questions about a dataset using agate.

The data will be using is a copy of the `National Registery of Exonerations <http://www.law.umich.edu/special/exoneration/Pages/detaillist.aspx>`_ made on August 28th, 2015. This dataset lists individuals who are known to have been exonerated after having been wrongly convicted. At the time the data was exported there were 1,651 entries in the registry.

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

First launch the Python interpreter::

    python

Now let's import our dependencies:

.. code-block:: python

    import csv
    import agate

.. note::

    You should really be using `csvkit <http://csvkit.readthedocs.org/>`_ (agate's sister project) to load CSV files, but here we stick with the builtin `csv` module because it comes with Python so everyone already has it.

Defining the columns
====================

agate requires us to give it some information about each column in our dataset. No effort is made to determine these types automatically, however, :class:`.TextType` is always a safe choice if you aren't sure what kind of data is in a column.

First we create instances of the column types we will be using:

.. code-block:: python

    text_type = agate.TextType()
    number_type = agate.NumberType()
    boolean_type = agate.BooleanType()

Then we define the names and types of the columns that are in our dataset:

.. code-block:: python

    COLUMNS = (
        ('last_name', text_type),
        ('first_name', text_type),
        ('age', number_type),
        ('race', text_type),
        ('state', text_type),
        ('tags', text_type),
        ('crime', text_type),
        ('sentence', text_type),
        ('convicted', number_type),
        ('exonerated', number_type),
        ('dna', boolean_type),
        ('dna_essential', text_type),
        ('mistaken_witness', boolean_type),
        ('false_confession', boolean_type),
        ('perjury', boolean_type),
        ('false_evidence', boolean_type),
        ('official_misconduct', boolean_type),
        ('inadequate_defense', boolean_type),
    )

    COLUMN_NAMES = [c[0] for c in COLUMNS]
    COLUMN_TYPES = [c[1] for c in COLUMNS]

You'll notice here that we define the names and types as pairs (tuples), but then use a couple fancy list comprehensions to split the pairs into two lists. The table creation function we'll be using next expects two lists, but I find it's convenient to define them as pairs and then split them up.

.. note::

    The column names defined here do not necessarily need to match those found in your CSV file. I've kept them consistent in this example for clarity.

Loading data from a CSV
=======================

Now let's read the data in the CSV file and use it to create the table.

.. code-block:: python

    with open('exonerations-20150828.csv') as f:
        # Create a CSV reader
        reader = csv.reader(f)

        # Skip header
        next(reader)

        # Create the table
        exonerations = agate.Table(reader, COLUMN_TYPES, COLUMN_NAMES)

:class:`.Table` will accept any array (iterable) of rows (iterables) as its first argument. In this case we're using a CSV reader.

.. note::

    The data is copied when the table is constructed so it safe to close the file handle immediately.

Aggregating column data
=======================

Analysis begins with questions, so that's how we'll learn about agate.

Question: **How many exonerations involved a false confession?**

Answering this question involves counting the number of "True" values in the ``false_confession`` column. When we created the table we specified that the data in this column was :class:`.BooleanType`. Because of this, agate has taken care of coercing the original text data from the CSV into Python's ``True`` and ``False`` values.

We'll answer the question using :class:`.Count` which is a type of :class:`.Aggregation`. Aggregations in agate are used to perform "column-wise" calculations. That is, they derive a new single value from the contents of a column. In the case of :class:`.Count`, it will tell us how many times a particular value appears in the column.

An :class:`.Aggregation` is applied to a column of a table. You can access the columns of a table using the :attr:`.Table.columns` attribute.

Putting it together looks like this:

.. code-block:: python

    num_false_confessions = exonerations.columns['false_confession'].aggregate(agate.Count(True))

    print(num_false_confessions)

::

    211

Let's look at another example, this time using a numerical aggregation.

Question: **What was the median age of exonerated indviduals at time of arrest?**

.. code-block:: python

    median_age = exonerations.columns['age'].aggregate(agate.Median())

    print(median_age)

Answer:

::

    agate.exceptions.NullComputationError

Apparently, not every exonerated individual in the data has a value for the ``age`` column. The :class:`.Median` statistical operation has no standard way of accounting for null values, so its caused an error.

Question: **How many individuals do not have an age specified in the data?**

.. code-block:: python

    num_without_age = exonerations.columns['age'].aggregate(agate.Count(None))

    print(num_without_age)

Answer:

::

    9

Only nine rows in this dataset don't have age, so it's still useful to compute a median, but to do this we'll need to filter out those null values first.

Each column in :attr:`.Table.columns` is a subclass of :class:`.Column`, such as :class:`.NumberColumn` or :class:`.TextColumn`. As we've seen with :class:`.Median`, different aggregations can be applied depending on the column type and, in this case, its contents.

If none of the provided aggregations suit your needs you can also easily create your own by subclassing :class:`.Aggregation`. See the API documentation for :mod:`.aggregations` to see all of the implemented types.

Selecting and filtering data
============================

So how can we answer our question about median age? First, we need to filter the data to only those rows that don't contain nulls.

Agate's :class:`.Table` class provides a full suite of these "SQL-like" operations, including :meth:`.Table.select` for grabbing specific columns, :meth:`.Table.where` for selecting particular rows and :meth:`.Table.group_by` for grouping rows by common values.

Let's filter our exonerations table to only those individuals that have an age specified.

.. code-block:: python

    with_age = exonerations.where(lambda row: row['age'] is not None)

You'll notice we provide a :keyword:`lambda` (anonymous) function to the :meth:`.Table.where`. This function is applied to each row and if it returns ``True``, the row is included in the output table.

A crucial thing to understand about these methods is that they return **new tables**. In our example above ``exonerations`` was a :class:`.Table` instance and we applied :meth:`.Table.where`, so ``with_age`` is a :class:`Table` too. The tables themselves are immutable. You can create new tables, but you can never modify them.

We can verify this did what we expected by counting the rows in the original table and rows in the new table:

.. code-block:: python

    old = len(exonerations.rows)
    new = len(with_age.rows)

    print(old - new)

::

    9

Nine rows were removed, which is how many we knew had nulls for the age column.

So, what **is** the median age of these individuals?

.. code-block:: python

    median_age = with_age.columns['age'].aggregate(agate.Median())

    print(median_age)

::

    26

Computing new columns
=====================

In addition to "column-wise" calculations there are also "row-wise" calculations. These calculations go through a :class:`.Table` row-by-row and derive a new column using the existing data. To perform row calculations in agate we use subclasses of :class:`.Computation`.

When one or more instances of :class:`.Computation` are applied to a :class:`.Table`, a new table is created with additional columns.

Question: **How long did individuals remain in prison before being exonerated?**

To answer this question we will apply the :class:`.Change` computation to the ``convicted`` and ``exonerated`` columns. All that :class:`.Change` does is compute the difference between two numbers. (In this case each of these columns contains an integer year, but agate does have features for working with dates too.)

.. code-block:: python

    with_years_in_prison = exonerations.compute([
        ('years_in_prison', agate.Change('convicted', 'exonerated'))
    ])

    median_years = with_years_in_prison.columns['years_in_prison'].aggregate(agate.Median())

    print(median_years)

::

    8

The median number of years an exonerated individual spent in prison was 8 years.

Sometimes, the built-in computations, such as :class:`.Change` won't suffice. In this case, you can use the generic :class:`.Formula` to compute a column based on an arbitrary function. This is somewhat analogous to Excel's cell formulas.

For instance, this example will create a ``full_name`` column from the ``first_name`` and ``last_name`` columns in the data:

.. code-block:: python

    full_names = exonerations.compute([
        ('full_name', agate.Formula(text_type, lambda row: '%(first_name)s %(last_name)s' % row)
    ])

For efficiencies sake, agate allows you to perform several computations at once.

.. code-block:: python

    with_computations = exonerations.compute([
        ('years_in_prison', agate.Change('convicted', 'exonerated')),
        ('full_name', agate.Formula(text_type, lambda row: '%(first_name)s %(last_name)s' % row)
    ])

If :class:`.Formula` still is not flexible enough (for instance, if you need to compute a new row based on the distribution of data in a column) you can always implement your own subclass of :class:`.Computation`. See the API documentation for :mod:`.computations` to see all of the supported ways to compute new data.

Sorting and slicing
===================

Question: **Who are the ten exonerated individuals who were youngest at the time they were arrested?**

Remembering that methods of tables return tables, we will use :meth:`.Table.order_by` to sort our table:

.. code-block:: python

    sorted_by_age = exonerations.order_by('age')

We can then use Python's slice syntax to get a subset of the rows in the table.

.. code-block:: python

    youngest_ten = sorted_by_age.rows[:10]

The variable ``youngest_ten`` now contains a list of :class:`.Row` objects. It is important to note that slicing :attr:`.Table.rows` does not return a new table. If you want get a subset of rows as a table use :meth:`.Table.where` or construct a new ``Table`` from the resulting list of rows.

Now let's print some information about the resulting rows:

.. code-block:: python

    for row in youngest_ten:
        print('%(first_name)s %(last_name)s (%(age)i) %(crime)s' % row)

::

    Lacresha Murray (11) Murder
    Johnathan Adams (12) Murder
    Anthony Harris (12) Murder
    Tyler Edmonds (13) Murder
    Zachary Handley (13) Arson
    Thaddeus Jimenez (13) Murder
    Jerry Pacek (13) Murder
    Jonathan Barr (14) Murder
    Dominique Brim (14) Assault
    Timothy Brown (14) Murder

If you find it impossible to believe that an eleven year-old was convicted of murder, I encourage you to read the Registry's `description of the case <http://www.law.umich.edu/special/exoneration/Pages/casedetail.aspx?caseid=3499>`_.

Grouping and aggregating
========================

Question: **Which state has seen the most exonerations?**

This question can't be answered by operating on a single column. What we need is the equivalent of SQL's ``GROUP BY``. agate supports a full set of SQL-like operations on tables. Unlike SQL, agate breaks grouping and aggregation into two discrete steps.

First, we use :meth:`.Table.group_by` to group the data by state.

.. code-block:: python

    by_state = exonerations.group_by('state')

This takes our original :class:`.Table` and groups it into a :class:`.TableSet`, which contains one table per county. Now we need to aggregate the total for each state. This works in a very similar way to how it did when we were aggregating columns of a single table.

.. code-block:: python

    state_totals = by_state.aggregate()

    sorted_totals = totals.order_by('count', reverse=True)

    for row in sorted_totals.rows[:5]:
        print('%(group)s: %(count)i' % row)

::

    TX: 212
    NY: 202
    CA: 154
    IL: 153
    MI: 60

Unsurpringly, the results appear roughly proportional to population.

Because we passed no arguments, :meth:`.TableSet.aggregate` did nothing except group the data and count the elements in each group, but the possiblities are much bigger.

Question: **What state has the longest median time in prison prior to exoneration?**

This is a much more complicated question that's going to pull together a lot of the features we've been using. We'll repeat the computations we applied before, but this time we're going to roll those computations up in our group and take the :class:`.Median` of each group. Then we'll sort the data and see where people have been stuck in prison the longest.

.. code-block:: python

    with_years_in_prison = exonerations.compute([
        ('years_in_prison', agate.Change('convicted', 'exonerated'))
    ])

    state_totals = with_years_in_prison.group_by('state')

    medians = totals.aggregate([
        ('years_in_prison', Median(), 'median_years_in_prison')
    ])

    sorted_medians = medians.order_by('median_years_in_prison', reverse=True)

    for row in sorted_medians.rows[:5]:
        print('%(group)s: %(median_years_in_prison)i' % row)

::

    DC: 27
    NE: 20
    ID: 19
    VT: 18
    LA: 16

DC? Nebraska? Idaho? What accounts for these states having the longest times in prison before exoneration? I have no idea and the data won't tell us. At this point you probably need to make some phone calls.

As with :meth:`.Table.aggregate` and :meth:`.Table.compute`, the :meth:`.TableSet.aggregate`: method takes a list of aggregations to perform. You can aggregate as many columns as you like in a single step and they will all appear in the output table.

Where to go next
================

This tutorial only scratches the surface of agate's features. For many more ideas on how to apply agate, check out the :doc:`cookbook`, which includes dozens of examples showing how to substitute agate for common operations used in Excel, SQL, R and more.
