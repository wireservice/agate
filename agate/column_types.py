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

#: String values which will be automatically cast to :code:`None`.
NULL_VALUES = ('', 'na', 'n/a', 'none', 'null', '.')

#: String values which will be automatically cast to :code:`True`.
TRUE_VALUES = ('yes', 'y', 'true', 't')

#: String values which will be automatically cast to :code:`False`.
FALSE_VALUES = ('no', 'n', 'false', 'f')

class ColumnType(object): #pragma: no cover
    """
    Base class for column data types.
    """
    def _create_column(self, table, index):
        raise NotImplementedError

class BooleanType(ColumnType):
    """
    Column type for :class:`BooleanColumn`.
    """
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

            if d_lower in NULL_VALUES:
                return None

            if d_lower in TRUE_VALUES:
                return True

            if d_lower in FALSE_VALUES:
                return False

        raise CastError('Can not convert value %s to bool for BooleanColumn.' % d)

    def _create_column(self, table, index):
        from agate.columns import BooleanColumn

        return BooleanColumn(table, index)

class DateType(ColumnType):
    """
    Column type for :class:`DateColumn`.
    """
    def __init__(self, date_format=None):
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

            if d.lower() in NULL_VALUES:
                return None

        if self.date_format:
            return datetime.datetime.strptime(d, self.date_format).date()

        return parse(d).date()

    def _create_column(self, table, index):
        from agate.columns import DateColumn

        return DateColumn(table, index)

class DateTimeType(ColumnType):
    """
    Column type for :class:`DateTimeColumn`.
    """
    def __init__(self, datetime_format=None):
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

            if d.lower() in NULL_VALUES:
                return None

        if self.datetime_format:
            return datetime.datetime.strptime(d, self.datetime_format)

        return parse(d)

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

            if d.lower() in NULL_VALUES:
                return None

        seconds = pytimeparse.parse(d)

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

            if d.lower() in NULL_VALUES:
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

            if d.lower() in NULL_VALUES:
                return None

        return six.text_type(d)

    def _create_column(self, table, index):
        from agate.columns import TextColumn

        return TextColumn(table, index)
