#!/usr/bin/env python

try:
    from cdecimal import Decimal, InvalidOperation
except ImportError: #pragma: no cover
    from decimal import Decimal, InvalidOperation
    
import six

from agate.column_types.base import *
from agate.exceptions import CastError

class NumberType(ColumnType):
    """
    Column type for :class:`NumberColumn`.
    """
    def test(self, d):
        """
        Test, for purposes of type inference, if a string value could possibly
        be valid for this column type.
        """
        d = d.replace(',' ,'').strip()

        if d.lower() in self.null_values:
            return True

        try:
            Decimal(d)
            return True
        except InvalidOperation:
            return False

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
