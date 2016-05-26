#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from cdecimal import Decimal, InvalidOperation
except ImportError:  # pragma: no cover
    from decimal import Decimal, InvalidOperation

from babel.core import Locale
import six

from agate.data_types.base import DataType
from agate.exceptions import CastError

#: A list of currency symbols sourced from `Xe <http://www.xe.com/symbols.php>`_.
DEFAULT_CURRENCY_SYMBOLS = [u'؋', u'$', u'ƒ', u'៛', u'¥', u'₡', u'₱', u'£', u'€', u'¢', u'﷼', u'₪', u'₩', u'₭', u'₮', u'₦', u'฿', u'₤', u'₫']

POSITIVE = Decimal('1')
NEGATIVE = Decimal('-1')


class Number(DataType):
    """
    Data representing numbers.

    :param locale:
        A locale specification such as :code:`en_US` or :code:`de_DE` to use
        for parsing formatted numbers.
    :param group_symbol:
        A grouping symbol used in the numbers. Overrides the value provided by
        the specified :code:`locale`.
    :param decimal_symbol:
        A decimal separate symbol used in the numbers. Overrides the value
        provided by the specified :code:`locale`.
    :param currency_symbols:
        A sequence of currency symbols to strip from numbers.
    """
    def __init__(self, locale='en_US', group_symbol=None, decimal_symbol=None, currency_symbols=DEFAULT_CURRENCY_SYMBOLS, **kwargs):
        super(Number, self).__init__(**kwargs)

        self.locale = Locale.parse(locale)

        self.currency_symbols = currency_symbols
        self.group_symbol = group_symbol or self.locale.number_symbols.get('group', ',')
        self.decimal_symbol = decimal_symbol or self.locale.number_symbols.get('decimal', '.')

    def cast(self, d):
        """
        Cast a single value to a :class:`decimal.Decimal`.

        :returns:
            :class:`decimal.Decimal` or :code:`None`.
        """
        if isinstance(d, Decimal) or d is None:
            return d

        t = type(d)

        if t is int:
            return Decimal(d)
        elif six.PY2 and t is long:
            return Decimal(d)
        elif t is float:
            return Decimal(repr(d))
        elif not isinstance(d, six.string_types):
            raise CastError('Can not parse value "%s" as Decimal.' % d)

        d = d.strip()

        if d.lower() in self.null_values:
            return None

        d = d.strip('%')

        if len(d) > 0 and d[0] == '-':
            d = d[1:]
            sign = NEGATIVE
        else:
            sign = POSITIVE

        for symbol in self.currency_symbols:
            d = d.strip(symbol)

        d = d.replace(self.group_symbol, '')
        d = d.replace(self.decimal_symbol, '.')

        try:
            return Decimal(d) * sign
        except InvalidOperation:
            pass

        raise CastError('Can not parse value "%s" as Decimal.' % d)

    def jsonify(self, d):
        if d is None:
            return d

        return float(d)
