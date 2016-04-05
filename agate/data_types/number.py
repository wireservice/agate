#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

from babel import localedata
from babel.core import Locale
from babel.numbers import parse_decimal
import six

from agate.data_types.base import DataType
from agate.exceptions import CastError

CURRENCY_SYMBOLS = list(localedata.load('root')['currency_symbols'].values())
CURRENCY_SYMBOLS.append(u'¢')

class Number(DataType):
    """
    Data representing numbers.

    :param locale:
        A locale specification such as :code:`en_US` or :code:`de_DE` to use
        for parsing formatted numbers.
    """
    def __init__(self, locale='en_US', **kwargs):
        super(Number, self).__init__(**kwargs)

        self.locale = Locale.parse(locale)

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
        elif isinstance(d, six.string_types):
            sign = Decimal(1)
            d = d.strip()
            d = d.strip('%')

            if len(d) > 0 and d[0] == '-':
                d = d[1:]
                sign = Decimal(-1)

            for symbol in CURRENCY_SYMBOLS:
                if d[:len(symbol)] == symbol:
                    d = d[len(symbol):]
                if d[(len(d) - len(symbol)):] == symbol:
                    d = d[:(len(d) - len(symbol))]

            if d.lower() in self.null_values:
                return None
        else:
            raise CastError('Can not parse value "%s" as Decimal.' % d)

        try:
            return parse_decimal(d, self.locale) * sign
        except:
            pass

        raise CastError('Can not parse value "%s" as Decimal.' % d)

    def jsonify(self, d):
        if d is None:
            return d

        return float(d)
