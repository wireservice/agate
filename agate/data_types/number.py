#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

from babel.numbers import parse_decimal
import six

from agate.data_types.base import DataType
from agate.exceptions import CastError

#: A list of currency symbols sourced from `Xe <http://www.xe.com/symbols.php>`_.
CURRENCY_SYMBOLS = [u'؋', u'$', u'ƒ', u'៛', u'¥', u'₡', u'₱', u'£', u'€', u'¢', u'﷼', u'₪', u'₩', u'₭', u'₮', u'₦', u'฿', u'₤', u'₫']

class Number(DataType):
    """
    Data type representing numbers.

    :param locale: A locale specification such as :code:`en_US` or
        :code:`de_DE` to use for parsing formatted numbers.
    :param display_precision: An integer specifying how many decimal places to
        include when formatting this column for display. (Such as when using
        :class:`.Table.pretty_print`.)
    """
    def __init__(self, locale='en_US', display_precision=2, **kwargs):
        super(Number, self).__init__(**kwargs)

        self._locale = locale
        self._display_precision = display_precision

    def test(self, d):
        """
        Test, for purposes of type inference, if a string value could possibly
        be valid for this column type.
        """
        d = d.strip()
        d = d.strip('%')

        for symbol in CURRENCY_SYMBOLS:
            d = d.strip(symbol)

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
            raise CastError('Can not convert float to Decimal. Convert data to string first!')
        elif isinstance(d, six.string_types):
            d = d.strip()

            if d.lower() in self.null_values:
                return None

        try:
            return parse_decimal(d, self._locale)
        except:
            raise CastError('Can not parse value "%s" as Decimal.' % d)
