import dataclasses
import typing

from anymerge import _predicates
from anymerge._typing_utils import extract_reducer, get_base_type
from anymerge.exceptions import AnyMergeTypeError
from anymerge.models import DEFAULT_REDUCER, FieldInfo, ReducerInfo

T = typing.TypeVar("T")


# TODO: Cache the results of this function
def collect_fields(
    cls_or_instance: typing.Any,
) -> dict[str, FieldInfo]:
    if _predicates.is_dataclass(cls_or_instance):
        return {
            field.name: FieldInfo(
                name=field.name,
                base_type=get_base_type(field.type),
                reducers=extract_reducer(field.type),
            )
            for field in dataclasses.fields(cls_or_instance)
        }

    if _predicates.is_typeddict(cls_or_instance):
        type_hints = typing.get_type_hints(cls_or_instance, include_extras=True)
        return {
            field_name: FieldInfo(
                name=field_name,
                base_type=get_base_type(field),
                reducers=extract_reducer(field),
            )
            for field_name, field in type_hints.items()
        }

    if _predicates.is_pydantic(cls_or_instance):
        return {
            field_name: FieldInfo(
                name=field_name,
                base_type=get_base_type(field.annotation),
                reducers=(
                    [data for data in field.metadata if isinstance(data, ReducerInfo)] or None
                ),
            )
            for field_name, field in cls_or_instance.__pydantic_fields__.items()
        }

    if _predicates.is_pydantic_v1(cls_or_instance):
        return {
            field_name: FieldInfo(
                name=field_name,
                base_type=get_base_type(field.annotation),
                reducers=extract_reducer(field.annotation) or None,
            )
            for field_name, field in cls_or_instance.__fields__.items()
        }

    msg = f"Unsupported class type: {cls_or_instance}"
    raise AnyMergeTypeError(msg)


def collect_values(
    instance: typing.Any,
) -> dict[str, typing.Any]:
    if _predicates.is_dataclass(instance):
        return vars(instance)

    if _predicates.is_typeddict(instance):
        return instance

    if _predicates.is_pydantic(instance):
        return dict(instance)

    if _predicates.is_pydantic_v1(instance):
        return dict(instance)

    msg = f"Unsupported instance type: {instance}"
    raise AnyMergeTypeError(msg)


def apply_reducers(
    a: typing.Any,
    b: typing.Any,
    *,
    field_info: FieldInfo,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> typing.Any:
    if field_info.reducers is None:
        return default_reducer(a, b)

    for reducer in field_info.reducers:
        if reducer.deep:
            a = merge(a, b, default_reducer=reducer)
        else:
            a = reducer(a, b)
    return a


def merge(
    a: T,
    b: typing.Any,
    *,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> T:
    """
    Merge two instances of data models.

    Args:
        a: The first instance to merge. This should contain all the annotations with the reducer information.
        b: The second instance to merge.
        default_reducer: The default reducer to apply to fields.

    Returns:
        The merged instance.
    """
    fields = collect_fields(a)
    a_values = collect_values(a)
    b_values = collect_values(b)
    changes = {
        key: apply_reducers(
            a_values[key],
            value,
            field_info=fields[key],
            default_reducer=default_reducer,
        )
        for key, value in b_values.items()
        if key in fields
    }

    if _predicates.is_dataclass(a):
        return typing.cast(T, dataclasses.replace(a, **changes))

    # TODO: Implement TypedDict support

    if _predicates.is_pydantic(a):
        return typing.cast(T, a.model_copy(update=changes))

    if _predicates.is_pydantic_v1(a):
        return typing.cast(T, a.copy(update=changes))

    msg = f"Unsupported instance type: {a}"
    raise NotImplementedError(msg)
