#!/usr/bin/env python

"""
This module contains the :class:`ColumnType` class and its subclasses. These
types define how data should be converted during the creation of a
:class:`.Table`. Each subclass of :class:`ColumnType` is associated with a
subclass of :class:`.Column`. For instance, specifying that data is of
:class:`NumberType` will cause a :class:`.NumberColumn` to be created on the
table.
"""

import datetime

try:
    from cdecimal import Decimal, InvalidOperation
except ImportError: #pragma: no cover
    from decimal import Decimal, InvalidOperation

from dateutil.parser import parse
import pytimeparse
import six

from agate.exceptions import CastError

#: Default values which will be automatically cast to :code:`None`
DEFAULT_NULL_VALUES = ('', 'na', 'n/a', 'none', 'null', '.')

#: Default values which will be automatically cast to :code:`True`.
DEFAULT_TRUE_VALUES = ('yes', 'y', 'true', 't')

#: Default values which will be automatically cast to :code:`False`.
DEFAULT_FALSE_VALUES = ('no', 'n', 'false', 'f')

class ColumnType(object): #pragma: no cover
    """
    Base class for column data types.

    :param null_values: A sequence of values which should be cast to
        :code:`None` when encountered with this type.
    """
    def __init__(self, null_values=DEFAULT_NULL_VALUES):
        self.null_values = null_values

    def _create_column(self, table, index):
        raise NotImplementedError

class BooleanType(ColumnType):
    """
    Column type for :class:`BooleanColumn`.

    :param true_values: A sequence of values which should be cast to
        :code:`True` when encountered with this type.
    :param false_values: A sequence of values which should be cast to
        :code:`False` when encountered with this type.
    """
    def __init__(self, true_values=DEFAULT_TRUE_VALUES, false_values=DEFAULT_FALSE_VALUES, null_values=DEFAULT_NULL_VALUES):
        super(BooleanType, self).__init__(null_values=null_values)

        self.true_values = true_values
        self.false_values = false_values

    def cast(self, d):
        """
        Cast a single value to :class:`bool`.

        :param d: A value to cast.
        :returns: :class:`bool` or :code:`None`.
        """
        if isinstance(d, bool) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.replace(',' ,'').strip()

            d_lower = d.lower()

            if d_lower in self.null_values:
                return None

            if d_lower in self.true_values:
                return True

            if d_lower in self.false_values:
                return False

        raise CastError('Can not convert value %s to bool for BooleanColumn.' % d)

    def _create_column(self, table, index):
        from agate.columns import BooleanColumn

        return BooleanColumn(table, index)

class DateType(ColumnType):
    """
    Column type for :class:`DateColumn`.
    """
    def __init__(self, date_format=None, null_values=DEFAULT_NULL_VALUES):
        super(DateType, self).__init__(null_values=null_values)

        self.date_format = date_format

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.date`.

        :param date_format: An optional :func:`datetime.strptime`
            format string for parsing dates in this column.
        :returns: :class:`datetime.date` or :code:`None`.
        """
        if isinstance(d, datetime.date) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        if self.date_format:
            return datetime.datetime.strptime(d, self.date_format).date()

        try:
            return parse(d).date()
        except (TypeError, ValueError):
            raise CastError('Can not parse value "%s" to as datetime for DateColumn.' % d)

    def _create_column(self, table, index):
        from agate.columns import DateColumn

        return DateColumn(table, index)

class DateTimeType(ColumnType):
    """
    Column type for :class:`DateTimeColumn`.
    """
    def __init__(self, datetime_format=None, null_values=DEFAULT_NULL_VALUES):
        super(DateTimeType, self).__init__(null_values=null_values)

        self.datetime_format = datetime_format

    def cast(self, d):
        """
        Cast a single value to a :class:`datetime.datetime`.

        :param date_format: An optional :func:`datetime.strptime`
            format string for parsing datetimes in this column.
        :returns: :class:`datetime.datetime` or :code:`None`.
        """
        if isinstance(d, datetime.datetime) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        if self.datetime_format:
            return datetime.datetime.strptime(d, self.datetime_format)

        try:
            return parse(d)
        except (TypeError, ValueError):
            raise CastError('Can not parse value "%s" to as datetime for DateTimeColumn.' % d)

    def _create_column(self, table, index):
        from agate.columns import DateTimeColumn

        return DateTimeColumn(table, index)

class TimeDeltaType(ColumnType):
    """
    Column type for :class:`datetime.timedelta`.
    """
    def cast(self, d):
        """
        Cast a single value to :class:`datetime.timedelta`.

        :param d: A value to cast.
        :returns: :class:`datetime.timedelta` or :code:`None`
        """
        if isinstance(d, datetime.timedelta) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        seconds = pytimeparse.parse(d)

        if seconds is None:
            raise CastError('Can not parse value "%s" to as timedelta for TimeDeltaColumn.' % d)

        return datetime.timedelta(seconds=seconds)

    def _create_column(self, table, index):
        from agate.columns import TimeDeltaColumn

        return TimeDeltaColumn(table, index)

class NumberType(ColumnType):
    """
    Column type for :class:`NumberColumn`.
    """
    def cast(self, d):
        """
        Cast a single value to a :class:`decimal.Decimal`.

        :returns: :class:`decimal.Decimal` or :code:`None`.
        :raises: :exc:`.CastError`
        """
        if isinstance(d, Decimal) or d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.replace(',' ,'').strip()

            if d.lower() in self.null_values:
                return None

        if isinstance(d, float):
            raise CastError('Can not convert float to Decimal for NumberColumn. Convert data to string first!')

        try:
            return Decimal(d)
        except InvalidOperation:
            raise CastError('Can not convert value "%s" to Decimal for NumberColumn.' % d)

    def _create_column(self, table, index):
        from agate.columns import NumberColumn

        return NumberColumn(table, index)

class TextType(ColumnType):
    """
    Column type for :class:`TextColumn`.
    """
    @classmethod
    def test(cls, d):
        return True

    def cast(self, d):
        """
        Cast a single value to :func:`unicode` (:func:`str` in Python 3).

        :param d: A value to cast.
        :returns: :func:`unicode` (:func:`str` in Python 3) or :code:`None`
        """
        if d is None:
            return d

        if isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        return six.text_type(d)

    def _create_column(self, table, index):
        from agate.columns import TextColumn

        return TextColumn(table, index)
