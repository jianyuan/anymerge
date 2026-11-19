import typing

import pydantic
import typing_extensions

from anymerge._typing_utils import (
    get_base_type,
    lenient_isinstance,
    lenient_issubclass,
)
from anymerge.adapters.base_adapter import BaseAdapter
from anymerge.models import FieldInfo, ReducerInfo

T = typing.TypeVar("T", bound=pydantic.BaseModel)


def is_pydantic_model(value: typing.Any) -> typing_extensions.TypeIs[pydantic.BaseModel]:
    return lenient_isinstance(value, pydantic.BaseModel) or (
        lenient_issubclass(value, pydantic.BaseModel)
    )


class PydanticAdapter(BaseAdapter[T], typing.Generic[T]):
    @classmethod
    def is_supported_type(cls, value: typing.Any) -> typing.TypeGuard[type[T]]:
        return is_pydantic_model(value)

    def get_fields(self) -> dict[typing.Any, FieldInfo]:
        return {
            field_name: FieldInfo(
                name=field_name,
                base_type=get_base_type(field.annotation),
                reducers=(
                    [data for data in field.metadata if isinstance(data, ReducerInfo)] or None
                ),
            )
            for field_name, field in self.model.__pydantic_fields__.items()
        }

    def get_values(self, value: T) -> dict[typing.Any, typing.Any]:
        return dict(value)

    def copy(self, value: T, *, changes: dict[typing.Any, typing.Any]) -> T:
        return value.model_copy(update=changes)
