#!/usr/bin/env python

try:
    from cdecimal import Decimal, InvalidOperation
except ImportError: #pragma: no cover
    from decimal import Decimal, InvalidOperation

from babel.numbers import parse_decimal
import six

from agate.column_types.base import *
from agate.exceptions import CastError

class NumberType(ColumnType):
    """
    Column type for :class:`NumberColumn`.

    :param locale: A locale specification such as :code:`en_US` or
        :code:`de_DE` to use for parsing formatted numbers.
    """
    def __init__(self, locale='en_US', **kwargs):
        super(NumberType, self).__init__(**kwargs)

        self._locale = locale

    def test(self, d):
        """
        Test, for purposes of type inference, if a string value could possibly
        be valid for this column type.
        """
        d = d.strip()

        if d.lower() in self.null_values:
            return True

        try:
            parse_decimal(d, self._locale)
            return True
        except:
            return False

    def cast(self, d):
        """
        Cast a single value to a :class:`decimal.Decimal`.

        :returns: :class:`decimal.Decimal` or :code:`None`.
        :raises: :exc:`.CastError`
        """
        if isinstance(d, Decimal) or d is None:
            return d
        elif isinstance(d, int):
            return Decimal(d)
        elif isinstance(d, float):
            raise CastError('Can not convert float to Decimal for NumberColumn. Convert data to string first!')
        elif isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        try:
            return parse_decimal(d, self._locale)
        except:
            raise CastError('Can not parse value "%s" as Decimal for NumberColumn.' % d)

    def create_column(self, table, index):
        from agate.columns import NumberColumn

        return NumberColumn(table, index)
