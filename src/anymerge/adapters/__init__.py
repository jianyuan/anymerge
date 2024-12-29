import typing

from anymerge.adapters.base_adapter import BaseAdapter
from anymerge.adapters.dataclass_adapter import DataclassAdapter
from anymerge.adapters.pydantic_adapter import PydanticAdapter
from anymerge.adapters.typeddict_adapter import TypedDictAdapter

ADAPTERS: list[type[BaseAdapter[typing.Any]]] = [
    DataclassAdapter,
    TypedDictAdapter,
    PydanticAdapter,
]

__all__ = [
    "ADAPTERS",
    "BaseAdapter",
    "DataclassAdapter",
    "PydanticAdapter",
    "TypedDictAdapter",
]
