from collections.abc import Callable as _Callable
from typing import TypeVar as _TypeVar

from agate.aggregations.base import Aggregation as Aggregation
from agate.data_types.base import DataType as _DataType
from agate.table import Table as _Table

_ValueT = _TypeVar("_ValueT")

class First(Aggregation[_ValueT]):
    _column_name: str
    _test: _Callable[[_ValueT], bool] | None

    def __init__(self, column_name: str, test: _Callable[[_ValueT], bool] | None = None) -> None: ...
    def get_aggregate_data_type(self, table: _Table) -> _DataType: ...
    def validate(self, table: _Table) -> None: ...
    def run(self, table: _Table) -> _ValueT: ...
