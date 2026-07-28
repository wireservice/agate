from collections.abc import Callable as _Callable
from typing import Generic as _Generic
from typing import TypeVar as _TypeVar

from agate.aggregations.base import Aggregation as Aggregation
from agate.columns import Column as _Column
from agate.data_types.base import DataType as _DataType
from agate.table import Table as _Table

_InputT = _TypeVar("_InputT")
_ResultT = _TypeVar("_ResultT")

class Summary(Aggregation[_ResultT], _Generic[_InputT, _ResultT]):
    _column_name: str
    _data_type: _DataType
    _func: _Callable[[_Column], _InputT]
    _cast: bool

    def __init__(
        self,
        column_name: str,
        data_type: _DataType,
        func: _Callable[[_Column], _InputT],
        cast: bool = True,
    ) -> None: ...
    def get_aggregate_data_type(self, table: _Table) -> _DataType: ...
    def run(self, table: _Table) -> _ResultT: ...
