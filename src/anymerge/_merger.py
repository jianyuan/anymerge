import dataclasses
import typing

import pydantic
import pydantic.v1

from anymerge._models import DEFAULT_REDUCER, ReducerInfo
from anymerge._typing_utils import extract_reducer
from anymerge.errors import AnyMergeTypeError

T = typing.TypeVar("T")


def collect_reducers(
    class_: typing.Any,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> dict[str, list[ReducerInfo]]:
    if dataclasses.is_dataclass(class_):
        return {
            field.name: extract_reducer(field.type) or [default_reducer]
            for field in dataclasses.fields(class_)
        }

    if typing.is_typeddict(class_):
        type_hints = typing.get_type_hints(class_, include_extras=True)
        return {
            field_name: extract_reducer(field) or [default_reducer]
            for field_name, field in type_hints.items()
        }

    if issubclass(class_, pydantic.BaseModel):
        return {
            field_name: (
                [data for data in field.metadata if isinstance(data, ReducerInfo)]
                or [default_reducer]
            )
            for field_name, field in class_.__pydantic_fields__.items()
        }

    if issubclass(class_, pydantic.v1.BaseModel):
        return {
            field_name: extract_reducer(field.annotation) or [default_reducer]
            for field_name, field in class_.__fields__.items()
        }

    msg = f"Unsupported class type: {class_}"
    raise AnyMergeTypeError(msg)


def merge(_a: T, _b: typing.Any) -> T:
    raise NotImplementedError
