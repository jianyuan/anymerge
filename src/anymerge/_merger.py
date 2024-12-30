import typing

from anymerge.adapters.utils import maybe_adapt_value
from anymerge.models import DEFAULT_REDUCER, FieldInfo, ReducerInfo

T = typing.TypeVar("T")


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
    adapted_a = maybe_adapt_value(a)
    adapted_b = maybe_adapt_value(b)
    fields = adapted_a.adapter.get_fields()
    a_values = adapted_a.get_values()
    b_values = adapted_b.get_values()
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

    return adapted_a.copy(changes=changes)
