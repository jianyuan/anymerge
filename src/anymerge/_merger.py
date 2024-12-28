import dataclasses
import typing

from anymerge import _predicates
from anymerge._typing_utils import extract_reducer
from anymerge.exceptions import AnyMergeTypeError
from anymerge.models import DEFAULT_REDUCER, ReducerInfo

T = typing.TypeVar("T")


# TODO: Cache the results of this function
def collect_reducers(
    cls_or_instance: typing.Any,
    *,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> dict[str, list[ReducerInfo]]:
    if _predicates.is_dataclass(cls_or_instance):
        return {
            field.name: extract_reducer(field.type) or [default_reducer]
            for field in dataclasses.fields(cls_or_instance)
        }

    if _predicates.is_typeddict(cls_or_instance):
        type_hints = typing.get_type_hints(cls_or_instance, include_extras=True)
        return {
            field_name: extract_reducer(field) or [default_reducer]
            for field_name, field in type_hints.items()
        }

    if _predicates.is_pydantic(cls_or_instance):
        return {
            field_name: (
                [data for data in field.metadata if isinstance(data, ReducerInfo)]
                or [default_reducer]
            )
            for field_name, field in cls_or_instance.__pydantic_fields__.items()
        }

    if _predicates.is_pydantic_v1(cls_or_instance):
        return {
            field_name: extract_reducer(field.annotation) or [default_reducer]
            for field_name, field in cls_or_instance.__fields__.items()
        }

    msg = f"Unsupported class type: {cls_or_instance}"
    raise AnyMergeTypeError(msg)


def collect_values(
    instance: typing.Any,
) -> dict[str, typing.Any]:
    if _predicates.is_dataclass(instance):
        return dataclasses.asdict(instance)

    if _predicates.is_typeddict(instance):
        return instance

    if _predicates.is_pydantic(instance):
        return instance.model_dump()

    if _predicates.is_pydantic_v1(instance):
        return instance.dict()

    msg = f"Unsupported instance type: {instance}"
    raise AnyMergeTypeError(msg)


def apply_reducers(
    a: typing.Any,
    b: typing.Any,
    *,
    reducers: list[ReducerInfo],
) -> typing.Any:
    # TODO: Handle deep merging
    for reducer in reducers:
        a = reducer(a, b)
    return a


def merge(
    a: T,
    b: typing.Any,
    *,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> T:
    if _predicates.is_dataclass(a):
        reducers = collect_reducers(a, default_reducer=default_reducer)
        original = collect_values(a)
        changes = {
            key: apply_reducers(original[key], value, reducers=reducers[key])
            for key, value in collect_values(b).items()
            if key in reducers
        }
        return typing.cast(T, dataclasses.replace(a, **changes))

    raise NotImplementedError
