import typing

from anymerge.adapters._utils import maybe_adapt_value
from anymerge.exceptions import AnyMergeValueError
from anymerge.models import DEFAULT_REDUCER, FieldInfo, Overwrite, ReducerInfo

T = typing.TypeVar("T")


def apply_reducers(
    a: typing.Any,
    b: typing.Any,
    *,
    field_info: FieldInfo,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> typing.Any:
    if isinstance(b, Overwrite):
        return b.value

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
    b_values = adapted_b.get_update_values()
    names = {alias: name for name, field in fields.items() for alias in field.aliases}
    allows_extra_fields = adapted_a.adapter.allows_extra_fields()
    changes = {}
    seen_keys: dict[typing.Any, typing.Any] = {}
    for key, value in b_values.items():
        name = names.get(key, key)
        if name in fields:
            field_info = fields[name]
        elif allows_extra_fields:
            field_info = FieldInfo(name=name, base_type=typing.Any, reducers=None)
        else:
            continue
        if name in seen_keys:
            msg = f"the update sets field {name!r} twice, as {seen_keys[name]!r} and {key!r}"
            raise AnyMergeValueError(msg)
        seen_keys[name] = key
        if name not in a_values:
            # Nothing to reduce with, e.g. a NotRequired key missing from a TypedDict base
            changes[name] = value.value if isinstance(value, Overwrite) else value
            continue
        try:
            changes[name] = apply_reducers(
                a_values[name],
                value,
                field_info=field_info,
                default_reducer=default_reducer,
            )
        except Exception as e:
            # Nested merges add one note per level, innermost first
            e.add_note(f"while merging field {name!r}")
            raise

    return adapted_a.copy(changes=changes)
