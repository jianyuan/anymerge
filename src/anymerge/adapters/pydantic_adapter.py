import typing

import pydantic
import pydantic.v1
import typing_extensions

from anymerge._typing_utils import extract_reducer, get_base_type
from anymerge.adapters.base_adapter import BaseAdapter
from anymerge.exceptions import AnyMergeTypeError
from anymerge.models import FieldInfo, ReducerInfo

T = typing.TypeVar("T", bound=pydantic.BaseModel | pydantic.v1.BaseModel)


def is_pydantic_v1_model(value: typing.Any) -> typing_extensions.TypeIs[pydantic.v1.BaseModel]:
    return isinstance(value, pydantic.v1.BaseModel) or (
        isinstance(value, type) and issubclass(value, pydantic.v1.BaseModel)
    )


def is_pydantic_v2_model(value: typing.Any) -> typing_extensions.TypeIs[pydantic.BaseModel]:
    return isinstance(value, pydantic.BaseModel) or (
        isinstance(value, type) and issubclass(value, pydantic.BaseModel)
    )


class PydanticAdapter(BaseAdapter[T], typing.Generic[T]):
    @classmethod
    def is_supported_type(cls, value: typing.Any) -> typing.TypeGuard[type[T]]:
        return is_pydantic_v2_model(value) or is_pydantic_v1_model(value)

    def get_fields(self) -> dict[typing.Any, FieldInfo]:
        if is_pydantic_v2_model(self.model):
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

        if is_pydantic_v1_model(self.model):
            return {
                field_name: FieldInfo(
                    name=field_name,
                    base_type=get_base_type(field.annotation),
                    reducers=extract_reducer(field.annotation) or None,
                )
                for field_name, field in self.model.__fields__.items()
            }

        raise AnyMergeTypeError(f"Unsupported Pydantic model type: {self.model}")

    def get_values(self, value: T) -> dict[typing.Any, typing.Any]:
        return dict(value)

    def copy(self, value: T, *, changes: dict[typing.Any, typing.Any]) -> T:
        if is_pydantic_v2_model(value):
            return typing.cast(T, value.model_copy(update=changes))

        if is_pydantic_v1_model(value):
            return typing.cast(T, value.copy(update=changes))

        raise AnyMergeTypeError(f"Unsupported Pydantic model type: {value}")
