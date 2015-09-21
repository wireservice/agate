===============
Dates and times
===============

agate includes robust support for working columns of data that are instances of :class:`datetime.date`, :class:`datetime.datetime` or :class:`datetime.timedelta`.

Infer a date format
===================

By default, agate will attempt to infer the format of a date column:

.. code-block:: python

    text_type = agate.Text()
    date_type = agate.Date()

    columns = (
        ('name', text_type),
        ('date', date_type)
    )

    table = agate.Table.from_csv('events.csv', columns)

Specify a date format
=====================

In some cases, it may not be possible to automatically parse the format of a date. In this case you can specify a :meth:`datetime.datetime.strptime` formatting string to specify how the dates should be parsed. For example, if your dates were formatted as "15-03-15" (March 15th, 2015) then you could specify:

.. code-block:: python

    date_type = agate.Date('%d-%m-%y')

Another use for this feature is if you have a column that contains extraneous data. For instance, imagine that your column contains hours and minutes, but they are always zero. It would make more sense to load that data as type :class:`.Date` and ignore the extra time information:

.. code-block:: python

    date_type = agate.Date('%m/%d/%Y 00:00')

.. _specify_a_timezone:

Specify a timezone
==================

Timezones are hard. Under normal circumstances (no arguments specified), agate will not try to parse timezone information, nor will it apply a timezone to the :class:`datetime.datetime` instances it creates. All the data it constructs will be *naive*. There are two ways to get timezone data into your agate columns.

The first is to use a format string, as shown above, and specify a pattern for timezone information:

.. code-block:: python

    datetime_type = agate.DateTime('%Y-%m-%d %H:%M:%S%z')

The second way is to specify a timezone as an argument to the type constructor:

.. code-block:: python

    import pytz

    eastern = pytz.timezone('US/Eastern')
    datetime_type = agate.DateTime(timezone=eastern)

In this case all timezones that are processed will be set to have the Eastern timezone. Note, the will be **set**, not converted. You can not use this method to convert your timezones from UTC to another timezone. To do that see :ref:`convert_timezones`.

Calculate a time difference
=============================

See :ref:`difference_between_dates`.

Sort by date
============

See :ref:`sort_by_date`.

.. _convert_timezones:

Convert timezones
====================

If you load data from a spreadsheet in one timezone and you need to convert it to another, you can do this using a :class:`.Formula`. Your datetime column must have timezone data for the following example to work. See :ref:`specify_a_timezone`.

.. code-block:: python

    import pytz

    us_eastern = pytz.timezone('US/Eastern')
    datetime_type = agate.DateTime(timezone=us_eastern)

    columns = (
        ('what', text_type),
        ('when', datetime_type)
    )

    table = agate.Table.from_csv('events.csv', columns)

    rome = timezone('Europe/Rome')
    timezone_shifter = agate.Formula(lambda r: r['when'].astimezone(rome))

    table = agate.Table.compute([
        (timezone_shifter, 'when_in_rome')
    ])
