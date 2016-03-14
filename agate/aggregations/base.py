#!/usr/bin/env python

import six

from agate.exceptions import UnsupportedAggregationError


@six.python_2_unicode_compatible
class Aggregation(object):  # pragma: no cover
    """
    An operation that takes a table and produces a single value summarizing
    one of it's columns. Aggregations are invoked with
    :class:`.TableSet.aggregate`.

    When implementing a custom subclass, ensure that the values returned by
    :meth:`run` are of the type specified by :meth:`get_aggregate_data_type`.
    This can be ensured by using the :meth:`.DataType.cast` method. See
    :class:`Formula` for an example.
    """
    def __str__(self):
        """
        String representation of this column. May be used as a column name in
        generated tables.
        """
        return self.__class__.__name__

    def get_aggregate_data_type(self, table):
        """
        Get the data type that should be used when using this aggregation with
        a :class:`.TableSet` to produce a new column.

        Should raise :class:`.UnsupportedAggregationError` if this column does
        not support aggregation into a :class:`.TableSet`. (For example, if it
        does not return a single value.)
        """
        raise UnsupportedAggregationError()

    def validate(self, table):
        """
        Perform any checks necessary to verify this aggregation can run on the
        provided table without errors. This is called by
        :meth:`.Table.aggregate` before :meth:`run`.
        """
        pass

    def run(self, table):
        """
        Execute this aggregation on a given column and return the result.
        """
        raise NotImplementedError()
