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

For every column in our dataset journalism requires us to define a type. Because journalism is focused on specific analysis of data (rather than casual viewing), no effort is made to determine these types for you. However, :py:class:`journalism.columns.TextType` is always a safe choice if you aren't sure what is in a column.

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
    f = open('examples/realdata/ks_1033_data.csv')

    # Create a CSV reader
    reader = csv.reader(f)

    # Skip header
    next(reader)
    
    # Create the table
    table = journalism.Table(reader, COLUMN_TYPES, COLUMN_NAMES)

    # Close the file
    f.close()

:py:class:`journalism.table.Table` will accept any iterable (array) of iterables (rows)  as it's first argument. In this case we're using a CSV reader. Note that the data is copied when the table is constructed so it safe to close the file handler.

Filtering and column operations 
===============================

Now let's use journalism to answer our first question about this dataset: **What was the total cost of all shipments delivered to the Kansas City area?**


Answering this question will require two elements: first filtering the data to only those rows related to Kansas City and then summing the ``total_cost`` column of those rows.

First, let's filter the data to just the four counties that contain Kansas city:

.. code-block:: python

    kansas_city = table.where(lambda r: r['county'] in ('JACKSON', 'CLAY', 'CASS', 'PLATTE'))

You'll notice we provide a :py:obj:`lambda` (anonymous) function to the :py:meth:`journalism.table.Table.where`. This function is applied to each row and if it returns ``True``, the row is included in the output table.

A crucial thing to understand about journalism is that **table methods return tables**. (If you're familiar with `jQuery <https://jquery.com/>`_, this is analogous to the way the methods of the $ object work.) ``table`` was a :py:class:`journalism.table.Table` instance and we applied the ``where`` method, so ``kansas_city`` is too. **Tables themselves are immutable. You can not modify the data of a table--only create new tables from them.**

You can access a dictionary of the columns of a table using the ``columns`` attribute. Each column is a subclass of :py:class:`journalism.columns.Column` and has a variety of aggregation functions that can be applied to it such as ``min``, ``max``, ``sum``, etc. Which aggregation functions are available depends on the type of the column.

Let's sum the values in the ``total_cost`` column for the ``kansas_city`` table:

.. code-block:: python

    total = kansas_city.columns['total_cost'].sum()
    print(total)

::

    3716

To make sure this is clear, let's look at a second example. Question: **How many robots were purchased in Kansas?**

.. code-block:: python

    robots = table.where(lambda r: 'ROBOT' in (r['item_name'] or '')).columns['quantity'].sum()
    print(robots)

::

    14 

Sorting and slicing
===================

Question: **What are the five most recent purchases made in Kansas?**

Remembering that methods of tables return tables, let's use the :py:meth:`journalism.table.Table.order_by` method to sort our table and then grab the first five rows of the resulting table.

.. code-block:: python

    recent_five = table.order_by('ship_date', reverse=True).rows[:5]

The variable ``recent_five`` now contains a list of :py:class:`journalism.rows.Row` objects. (Slicing the ``rows`` class attribute does not return a table. If you want get a subset of rows as a table use :py:meth:`journalism.table.Table.where` or construct a new ``Table`` from the resulting list of rows. 

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

Aggregation
===========

Question: **Which five counties acquired the most items?**

This question can't be answered by operating on a single column. What we need is the equivalent of SQL's ``GROUP BY``. journalism supports a full set of SQL-like operations on tables. The one we want in this case is :py:meth:`journalism.table.Table.aggregate`:

.. code-block:: python

    totals = table.aggregate('county', (( 'total_cost', 'sum' ),)).order_by('total_cost_sum', reverse=True).rows[:5]

The first argument to :py:meth:`journalism.table.Table.aggregate` is a column to group by. The second argument is a list (or, in this case, tuple) of pairs of columns and operations to be applied. Any aggregate method that can be applied to a column can also be applied in an aggregate, simply specify the method name as a string. The output of ``aggregate`` is, naturally, a table, which can be ordered like any other table. Note that the output table includes an aggregate column which is named using the name of the input column plus an underscore and then the name of the operation that was applied. This allows multiple aggregations to be applied to the same column without confusion.

Let's print the details of the rows we've found:

.. code-block:: python

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

