import typing

from anymerge.adapters import ADAPTERS
from anymerge.exceptions import AnyMergeTypeError
from anymerge.models import DEFAULT_REDUCER, FieldInfo, ReducerInfo

T = typing.TypeVar("T")


# TODO: Cache the results of this function
def collect_fields(value: typing.Any) -> dict[str, FieldInfo]:
    for adapter_cls in ADAPTERS:
        if adapter_cls.is_supported_type(value):
            return adapter_cls(value).get_fields()

    msg = f"Unsupported class type: {value}"
    raise AnyMergeTypeError(msg)


def collect_values(value: typing.Any) -> dict[str, typing.Any]:
    for adapter_cls in ADAPTERS:
        if adapter_cls.is_supported_type(value):
            return adapter_cls(value).get_values(value)

    msg = f"Unsupported instance type: {value}"
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

    for adapter_cls in ADAPTERS:
        if adapter_cls.is_supported_type(a):
            return adapter_cls(a).copy(a, changes=changes)

    msg = f"Unsupported instance type: {a}"
    raise NotImplementedError(msg)
