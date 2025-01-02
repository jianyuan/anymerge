from __future__ import annotations

import dataclasses
import typing

from anymerge._typing_utils import extract_reducer, get_base_type
from anymerge.adapters.base_adapter import BaseAdapter
from anymerge.exceptions import AnyMergeValueError
from anymerge.models import FieldInfo

if typing.TYPE_CHECKING:
    import _typeshed

T = typing.TypeVar("T", bound="_typeshed.DataclassInstance")


class DataclassAdapter(BaseAdapter[T], typing.Generic[T]):
    @classmethod
    def is_supported_type(cls, value: typing.Any) -> typing.TypeGuard[type[T]]:
        return dataclasses.is_dataclass(value)

    def get_fields(self) -> dict[typing.Any, FieldInfo]:
        if self.model is None:
            msg = "model is not set"
            raise AnyMergeValueError(msg)
        return {
            field.name: FieldInfo(
                name=field.name,
                base_type=get_base_type(field.type),
                reducers=extract_reducer(field.type),
            )
            for field in dataclasses.fields(self.model)
        }

    def get_values(self, value: T) -> dict[typing.Any, typing.Any]:
        return vars(value)

    def copy(self, value: T, *, changes: dict[typing.Any, typing.Any]) -> T:
        return dataclasses.replace(value, **changes)
