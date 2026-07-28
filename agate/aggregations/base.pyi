from typing import Generic as _Generic
from typing import TypeVar as _TypeVar

from agate.data_types.base import DataType as _DataType
from agate.exceptions import UnsupportedAggregationError as UnsupportedAggregationError
from agate.table import Table as _Table

_ResultT_co = _TypeVar("_ResultT_co", covariant=True)

class Aggregation(_Generic[_ResultT_co]):
    def __str__(self) -> str: ...
    def get_aggregate_data_type(self, table: _Table) -> _DataType | None: ...
    def validate(self, table: _Table) -> None: ...
    def run(self, table: _Table) -> _ResultT_co: ...
