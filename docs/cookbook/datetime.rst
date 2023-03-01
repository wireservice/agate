===============
Dates and times
===============

Specify a date format
=====================

By default agate will attempt to guess the format of a :class:`.Date` or :class:`.DateTime` column. In some cases, it may not be possible to automatically figure out the format of a date. In this case you can specify a :meth:`datetime.datetime.strptime` formatting string to specify how the dates should be parsed. For example, if your dates were formatted as "15-03-15" (March 15th, 2015) then you could specify:

.. code-block:: python

    date_type = agate.Date('%d-%m-%y')

Another use for this feature is if you have a column that contains extraneous data. For instance, imagine that your column contains hours and minutes, but they are always zero. It would make more sense to load that data as type :class:`.Date` and ignore the extra time information:

.. code-block:: python

    date_type = agate.Date('%m/%d/%Y 00:00')

.. _specify_a_timezone:

Specify a timezone
==================

Timezones are hard. Under normal circumstances (no arguments specified), agate will not try to parse timezone information, nor will it apply a timezone to the :class:`datetime.datetime` instances it creates. (They will be *naive* in Python parlance.) There are two ways to force timezone data into your agate columns.

The first is to use a format string, as shown above, and specify a pattern for timezone information:

.. code-block:: python

    datetime_type = agate.DateTime('%Y-%m-%d %H:%M:%S%z')

The second way is to specify a timezone as an argument to the type constructor:

.. code-block:: python

    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        # Fallback for Python < 3.9
        from backports.zoneinfo import ZoneInfo

    eastern = ZoneInfo('US/Eastern')
    datetime_type = agate.DateTime(timezone=eastern)

In this case all timezones that are processed will be set to have the Eastern timezone. Note, the timezone will be **set**, not converted. You cannot use this method to convert your timezones from UTC to another timezone. To do that see :ref:`convert_timezones`.

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

    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        # Fallback for Python < 3.9
        from backports.zoneinfo import ZoneInfo

    us_eastern = ZoneInfo('US/Eastern')
    datetime_type = agate.DateTime(timezone=us_eastern)

    column_names = ['what', 'when']
    column_types = [text_type, datetime_type]

    table = agate.Table.from_csv('events.csv', columns)

    rome = ZoneInfo('Europe/Rome')
    timezone_shifter = agate.Formula(lambda r: r['when'].astimezone(rome))

    table = agate.Table.compute([
        ('when_in_rome', timezone_shifter)
    ])
