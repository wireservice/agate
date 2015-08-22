#!/usr/bin/env python

from journalism.columns.base import *
from journalism.exceptions import CastError

#: String values which will be automatically cast to :code:`True`.
TRUE_VALUES = ('yes', 'y', 'true', 't')

#: String values which will be automatically cast to :code:`False`.
FALSE_VALUES = ('no', 'n', 'false', 'f')

class BooleanType(ColumnType):
    """
    Column type for :class:`BooleanColumn`.
    """
    def cast(self, d):
        """
        Cast a single value to :func:`bool`.

        :param d: A value to cast.
        :returns: :func:`bool` or :code:`None`.
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
        return BooleanColumn(table, index)

    def _create_column_set(self, tableset, index):
        return BooleanColumnSet(tableset, index)

class BooleanColumn(Column):
    """
    A column containing :func:`bool` data.
    """
    def __init__(self, *args, **kwargs):
        super(BooleanColumn, self).__init__(*args, **kwargs)

        self.any = BooleanAnyOperation(self)
        self.all = BooleanAllOperation(self)

class BooleanAnyOperation(ColumnOperation):
    """
    Returns :code:`True` if any value is :code:`True`.
    """
    def get_aggregate_column_type(self):
        return BooleanType()

    def __call__(self):
        return any(self._column._data())

class BooleanAllOperation(ColumnOperation):
    """
    Returns :code:`True` if all values are :code:`True`.
    """
    def get_aggregate_column_type(self):
        return BooleanType()

    def __call__(self):
        return all(self._column._data())
