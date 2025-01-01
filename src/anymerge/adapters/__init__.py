import typing

from anymerge.adapters.base_adapter import BaseAdapter
from anymerge.adapters.dataclass_adapter import DataclassAdapter
from anymerge.adapters.dict_adapter import DictAdapter
from anymerge.adapters.pydantic_adapter import PydanticAdapter
from anymerge.adapters.typeddict_adapter import TypedDictAdapter

ADAPTERS: list[type[BaseAdapter[typing.Any]]] = [
    DataclassAdapter,
    DictAdapter,
    PydanticAdapter,
    TypedDictAdapter,
]

__all__ = [
    "ADAPTERS",
    "BaseAdapter",
    "DataclassAdapter",
    "DictAdapter",
    "PydanticAdapter",
    "TypedDictAdapter",
]
