from __future__ import annotations

import typing as _typing

from agate.exceptions import UnsupportedAggregationError

if _typing.TYPE_CHECKING:
    from agate.data_types.base import DataType as _DataType
    from agate.table import Table as _Table

_ResultT_co = _typing.TypeVar("_ResultT_co", covariant=True)

# Parameterize for type checkers without adding typing.Generic to the runtime MRO.
if _typing.TYPE_CHECKING:
    class _AggregationTypingBase(_typing.Generic[_ResultT_co]):
        pass
else:
    class _NoRuntimeBase:
        def __mro_entries__(self, bases):
            return ()

    class _AggregationTypingBase:
        @classmethod
        def __class_getitem__(cls, item):
            return _NoRuntimeBase()


class Aggregation(_AggregationTypingBase[_ResultT_co]):  # pragma: no cover
    """
    Aggregations create a new value by summarizing a :class:`.Column`.

    Aggregations are applied with :meth:`.Table.aggregate` and
    :meth:`.TableSet.aggregate`.

    When creating a custom aggregation, ensure that the values returned by
    :meth:`.Aggregation.run` are of the type specified by
    :meth:`.Aggregation.get_aggregate_data_type`. This can be ensured by using
    the :meth:`.DataType.cast` method. See :class:`.Summary` for an example.
    """
    def __str__(self) -> str:
        """
        String representation of this column. May be used as a column name in
        generated tables.
        """
        return self.__class__.__name__

    def get_aggregate_data_type(self, table: _Table) -> _DataType | None:
        """
        Get the data type that should be used when using this aggregation with
        a :class:`.TableSet` to produce a new column.

        Should raise :class:`.UnsupportedAggregationError` if this column does
        not support aggregation into a :class:`.TableSet`. (For example, if it
        does not return a single value.)
        """
        raise UnsupportedAggregationError()

    def validate(self, table: _Table) -> None:
        """
        Perform any checks necessary to verify this aggregation can run on the
        provided table without errors. This is called by
        :meth:`.Table.aggregate` before :meth:`run`.
        """
        pass

    def run(self, table: _Table) -> _ResultT_co:
        """
        Execute this aggregation on a given column and return the result.
        """
        raise NotImplementedError()


if not _typing.TYPE_CHECKING:
    del _AggregationTypingBase
    del _NoRuntimeBase
