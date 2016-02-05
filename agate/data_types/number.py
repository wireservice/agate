#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
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

    :param locale:
        A locale specification such as :code:`en_US` or :code:`de_DE` to use
        for parsing formatted numbers.
    """
    def __init__(self, locale='en_US', **kwargs):
        super(Number, self).__init__(**kwargs)

        self.locale = locale

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
            d = d.strip()
            d = d.strip('%')

            for symbol in CURRENCY_SYMBOLS:
                d = d.strip(symbol)

            if d.lower() in self.null_values:
                return None
        else:
            raise CastError('Can not parse value "%s" as Decimal.' % d)

        try:
            return parse_decimal(d, self.locale)
        except:
            pass

        raise CastError('Can not parse value "%s" as Decimal.' % d)

    def jsonify(self, d):
        if d is None:
            return d

        return float(d)
