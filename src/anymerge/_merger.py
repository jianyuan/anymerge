import dataclasses
import typing

from anymerge import _predicates
from anymerge._typing_utils import extract_reducer
from anymerge.exceptions import AnyMergeTypeError
from anymerge.models import DEFAULT_REDUCER, ReducerInfo

T = typing.TypeVar("T")


def collect_reducers(
    cls: type[typing.Any],
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> dict[str, list[ReducerInfo]]:
    if _predicates.is_dataclass(cls):
        return {
            field.name: extract_reducer(field.type) or [default_reducer]
            for field in dataclasses.fields(cls)
        }

    if _predicates.is_typeddict(cls):
        type_hints = typing.get_type_hints(cls, include_extras=True)
        return {
            field_name: extract_reducer(field) or [default_reducer]
            for field_name, field in type_hints.items()
        }

    if _predicates.is_pydantic(cls):
        return {
            field_name: (
                [data for data in field.metadata if isinstance(data, ReducerInfo)]
                or [default_reducer]
            )
            for field_name, field in cls.__pydantic_fields__.items()
        }

    if _predicates.is_pydantic_v1(cls):
        return {
            field_name: extract_reducer(field.annotation) or [default_reducer]
            for field_name, field in cls.__fields__.items()
        }

    msg = f"Unsupported class type: {cls}"
    raise AnyMergeTypeError(msg)


def merge(_a: T, _b: typing.Any) -> T:
    raise NotImplementedError
