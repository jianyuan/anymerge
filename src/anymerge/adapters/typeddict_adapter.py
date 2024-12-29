import typing

from anymerge._typing_utils import extract_reducer, get_base_type
from anymerge.adapters.base_adapter import BaseAdapter
from anymerge.models import FieldInfo

T = typing.TypeVar("T", bound=dict[typing.Any, typing.Any])


class TypedDictAdapter(BaseAdapter[T], typing.Generic[T]):
    @classmethod
    def is_supported_type(cls, value: typing.Any) -> typing.TypeGuard[type[T]]:
        return typing.is_typeddict(value)

    def get_fields(self) -> dict[typing.Any, FieldInfo]:
        type_hints = typing.get_type_hints(self.model, include_extras=True)
        return {
            field_name: FieldInfo(
                name=field_name,
                base_type=get_base_type(field),
                reducers=extract_reducer(field),
            )
            for field_name, field in type_hints.items()
        }

    def get_values(self, value: T) -> dict[typing.Any, typing.Any]:
        return value

    def copy(self, value: T, *, changes: dict[typing.Any, typing.Any]) -> T:
        return typing.cast(T, {**value, **changes})
