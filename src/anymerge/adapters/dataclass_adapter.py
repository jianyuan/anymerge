from __future__ import annotations

import dataclasses
import typing

from anymerge._typing_utils import extract_reducer, get_base_type
from anymerge.adapters.base_adapter import BaseAdapter
from anymerge.exceptions import AnyMergeTypeError, AnyMergeValueError
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
        # Resolve string annotations, e.g. from `from __future__ import annotations`
        model_type = self.model if isinstance(self.model, type) else type(self.model)
        try:
            type_hints = typing.get_type_hints(model_type, include_extras=True)
        except NameError as e:
            msg = f"cannot resolve the type annotations of {model_type.__qualname__}: {e}"
            raise AnyMergeTypeError(msg) from e
        return {
            field.name: FieldInfo(
                name=field.name,
                base_type=get_base_type(type_hints[field.name]),
                reducers=extract_reducer(type_hints[field.name]),
            )
            for field in dataclasses.fields(self.model)
        }

    def get_values(self, value: T) -> dict[typing.Any, typing.Any]:
        # Read declared fields, since slots dataclasses have no __dict__ for vars()
        return {field.name: getattr(value, field.name) for field in dataclasses.fields(value)}

    def copy(self, value: T, *, changes: dict[typing.Any, typing.Any]) -> T:
        return dataclasses.replace(value, **changes)
