========
Tutorial
========

About this tutorial
===================

The best way to learn to use any tool is to actually use it. In this tutorial we will answer some basic questions about a dataset using journalism.

The data will be using is a subset of the United States Defense Logistic Agency Law Enforcement Support Office’s (LESO) 1033 Program dataset, which describes how surplus military arms have been distributed to local police forces. This data has been widely cited in the aftermath of the Ferguson, Missouri protests. The particular data we are using comes from an NPR report analyzing the data.

Installing journalism
=====================

Installing journalism is easy::

    sudo pip install journalism

.. note::

    If you're familiar with `virtualenv <http://virtualenv.readthedocs.org/en/latest/>`_, it's better to install journalism inside an env, in which case you should leave off the ``sudo`` in the previous command.

Getting the data
================

Let's start by creating a clean workspace::

    mkdir journalism_tutorial
    cd journalism_tutorial

Now let's fetch the data::

    curl -L -O https://github.com/onyxfish/journalism/raw/master/examples/realdata/ks_1033_data.csv

This data is for the state of Kansas.

Getting setup
=============

First launch the Python interpreter::

    python

Now let's import our dependencies:

.. code-block:: python

    import csv
    import journalism

.. note::

    You should really be using `csvkit <http://csvkit.readthedocs.org/>`_ (journalism's sister project) to load CSV files, but here we stick with the builtin `csv` module because everyone has it.

Defining the columns
====================

journalism requires us to define a type for each column in our dataset. No effort is made to determine these types automatically, however, :class:`.TextType` is always a safe choice if you aren't sure what is in a column.

First we create instances of the column types we will be using:

.. code-block:: python

    text_type = journalism.TextType()
    number_type = journalism.NumberType()
    date_type = journalism.DateType()

Then we define the names and types of the columns that are in our dataset:

.. code-block:: python

    COLUMNS = (
        ('state', text_type),
        ('county', text_type),
        ('fips', text_type),
        ('nsn', text_type),
        ('item_name', text_type),
        ('quantity', number_type),
        ('ui', text_type),
        ('acquisition_cost', number_type),
        ('total_cost', number_type),
        ('ship_date', date_type),
        ('federal_supply_category', text_type),
        ('federal_supply_category_name', text_type),
        ('federal_supply_class', text_type),
        ('federal_supply_class_name', text_type),
    )

    COLUMN_NAMES = [c[0] for c in COLUMNS]
    COLUMN_TYPES = [c[1] for c in COLUMNS]

You'll notice here that we define the names and types as pairs (tuples), but then use a list comprehension to split the pairs into two lists. The table creation function we'll be using next expects two lists, but I find it's convenient to define them as pairs and then split them up.

.. note::

    The column names defined here do not need to match those found in your data file. I've kept them consistent here for clarity.

Loading data from a CSV
=======================

Now let's read the data in the CSV file and use it to create the table.

.. code-block:: python

    # Open the file
    f = open('ks_1033_data.csv')

    # Create a CSV reader
    reader = csv.reader(f)

    # Skip header
    next(reader)

    # Create the table
    table = journalism.Table(reader, COLUMN_TYPES, COLUMN_NAMES)

    # Close the file
    f.close()

:class:`.Table` will accept any iterable (array) of iterables (rows)  as it's first argument. In this case we're using a CSV reader. Note that the data is copied when the table is constructed so it safe to close the file handler immediately.

Selecting and filtering data
============================

Now let's start to answer a first question about this dataset: **What was the total cost of all shipments delivered to the Kansas City area?**

Answering this question will require two parts: first filtering the data to only those rows related to Kansas City and then summing the ``total_cost`` column of those rows. Let's start by filtering the data to just the four counties that contain Kansas city:

.. code-block:: python

    kansas_city = table.where(lambda r: r['county'] in ('JACKSON', 'CLAY', 'CASS', 'PLATTE'))

You'll notice we provide a :keyword:`lambda` (anonymous) function to the :meth:`.Table.where`. This function is applied to each row and if it returns ``True``, the row is included in the output table.

:class:`.Table` provides a full suite of these "SQL-like" operations, including :meth:`.Table.select` for grabbing specific columns, :meth:`.Table.where` for selecting particular rows and :meth:`.Table.group_by` for subsetting rows.

A crucial thing to understand about these methods is that they return **new tables**. In our example above ``table`` was a :class:`.Table` instance and we applied :meth:`.Table.where`, so ``kansas_city`` is a :class:`Table` too. The tables themselves are immutable. You can create new tables, but you can never modify them.

Summarizing column data
=======================

In order to answer our question about the total cost of shipments to Kansas City we need to sum the costs, which is a column-wise operation. To perform column operations in journalism we will use a subclass of :class:`.Aggregation`.

An :class:`.Aggregation` is applied to a column of a table. You can access the columns of a table using the :attr:`.Table.columns` attribute. To sum the ``total_cost`` column we will aggregate using an instance of the :class:`.Sum` aggregator:

.. code-block:: python

    total = kansas_city.columns['total_cost'].aggregate(Sum())
    print(total)

::

    3716

Here is a second example. Question: **How many robots were purchased in Kansas?**

.. code-block:: python

    robot_count = table.where(lambda r: 'ROBOT' in (r['item_name'] or '')).columns['quantity'].aggregate(Sum())
    print(robot_count)

Answer:

::

    14

.. note::

    The ``(r['item_name'] or '')`` clause prevents an exception if the ``item_name`` column was ``None`` (blank) for any rows.

Each column in :attr:`.Table.columns` is a subclass of :class:`.Column`, such as :class:`.NumberColumn` or :class:`.TextColumn`. Different aggregations can be applied depending on the column type. For instance, descriptive statistics such as :class:`.Mean`, :class:`.Median` and :class:`.Mode` can only be applied to instances of :class:`.NumberColumn`. If none of the provided aggregations suit your needs you can also create your own create your own by subclassing :class:`.Aggregation`. See the API documentation for :mod:`.aggregations` to see all of the supported types.

Computing new columns
=====================

In addition to column-wise operations there are also many important row-wise data operations. These are operations which go through a :class:`.Table` row-by-row and compute a new column using the existing data. To perform row operations in journalism we use subclasses of :class:`.Computation`.

A :class:`.Computation` is applied to a :class:`.Table` and yields an entirely new table.
TKTK: question

.. code-block:: python

    # TODO: Computation example here

For efficiencies sake, journalism allows you to perform several computations at once.

.. code-block:: python

    # TODO: Multi-computation example here

Sometimes, the built-in computations won't suffice. In this case, you can use the generic :class:`.Formula` to compute a column based on an arbitrary function. This is somewhat analogous to Excel's cell formulas.

.. code-block:: python

    # TODO: Formula example

If :class:`.Formula` still isn't flexible enough (for instance, if you need to compute a new row based on the distribution of data in a column) you can always implement your own subclass of :class:`.Computation`. See the API documentation for :mod:`.computations` to see all of the supported ways to compute new data.

Sorting and slicing
===================

Question: **What are the five most recent purchases made in Kansas?**

Remembering that methods of tables return tables, let's use the :meth:`.Table.order_by` method to sort our table and then grab the first five rows of the resulting table.

.. code-block:: python

    recent_five = table.order_by('ship_date', reverse=True).rows[:5]

The variable ``recent_five`` now contains a list of :class:`.Row` objects. (Slicing the ``rows`` class attribute does not return a table. If you want get a subset of rows as a table use :meth:`.Table.where` or construct a new ``Table`` from the resulting list of rows.

Now let's print some information about the resulting rows:

.. code-block:: python

    for row in recent_five:
        text = '{}: {} {}, ${:,}'.format(row['ship_date'], row['quantity'], row['item_name'], row['total_cost'])
        print(text)

::

    2014-04-17: 1 ROBOT,EXPLOSIVE ORDNANCE DISPOSAL, $10,000
    2014-04-17: 1 ROBOT,EXPLOSIVE ORDNANCE DISPOSAL, $10,000
    2014-04-17: 1 ROBOT,EXPLOSIVE ORDNANCE DISPOSAL, $10,000
    2014-04-17: 1 HARDWARE KIT,ELECTRONIC EQUIPMENT, $13,999
    2014-03-25: 1 BICYCLE, EXERCISE, $0

Grouping and aggregating
========================

Question: **Which five counties acquired the most items?**

This question can't be answered by operating on a single column. What we need is the equivalent of SQL's ``GROUP BY``. journalism supports a full set of SQL-like operations on tables. Unlike SQL, we'll break grouping and aggregation into two distinct steps.

.. code-block:: python

    counties = table.group_by('county')

This command takes our original :class:`.Table` and groups it into a :class:`.TableSet`, which contains one table per county. Now we'll aggregate the totals for each group.

.. code-block:: python

    totals = counties.aggregate([
        ('total_cost', Sum(), 'total_cost_sum')
    ])

This takes our grouped ``TableSet``, computes the sum of the ``total_cost`` column for each ``Table`` in the set and then builds a new table containing the aggregate results. The new table will have the columns ``group``, ``count`` and ``total_sum_cost``. The first two columns always have the same names and the last one is generated based on the name of the column and the operation being applied.

The :meth:`.TableSet.aggregate`: function takes a list of operations to perform. You can aggregate as many columns as you like in a single step and they will all appear in the output table.

Lastly, we'll sort our new table and print the results.

.. code-block:: python

    totals = totals.order_by('total_cost_sum', reverse=True).rows[:5]

    for i, row in enumerate(totals):
        text = '#{}: {}, ${:,}'.format(i + 1, row['county'], row['total_cost_sum'])
        print(text)

::

    #1: SEDGWICK, $977,174.45
    #2: COFFEY, $691,749.03
    #3: MONTGOMERY, $447,581.2
    #4: JOHNSON, $420,628
    #5: SALINE, $245,450.24

Where to go next
================

This tutorial only scratches the surface of journalism's features. For many more ideas on how to apply journalism, check out the :doc:`cookbook`, which includes dozens of examples showing how to substitute journalism for common operations used in Excel, SQL, R and more.
