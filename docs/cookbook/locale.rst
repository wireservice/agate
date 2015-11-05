=======
Locales
=======

agate tries very hard to adequately support non-US, non-English users. This means properly handling foreign currencies, date formats, etc. To facilitate this, agate makes a hard distinction between *your* locale and the locale of *the data* you are working with. This allows you to work seamlessly with data from other countries.

Set your locale
===============

Specifying your current locale works the same as with any other Python module. Please see the :mod:`locale` documentation for more details. Changes to your locale will automatically change how agate data is printed to the console and serialized to CSV files, but will not effect how data is *parsed*. See :ref:`specify_locale_of_numbers` for that.

.. _specify_locale_of_numbers:

Specify locale of numbers
=========================

To correctly parse numbers from non-US locales, you can pass a :code:`locale` parameter to the :class:`.Number` constructor. For example, to parse Dutch numbers (which use a period to separate thousands and a comma to separate fractions):

.. code-block:: python

    dutch_numbers = agate.Number(locale='de_DE')

    column_names = ['city', 'population']
    column_types = [text_type, dutch_numbers]

    table = agate.Table.from_csv('dutch_cities.csv', columns)
