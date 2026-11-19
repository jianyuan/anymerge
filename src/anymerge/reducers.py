import dataclasses
import typing

from anymerge.types import ReducerCallable

T = typing.TypeVar("T")


def replace(_a: typing.Any, b: T, /) -> T:
    """Return the second argument."""
    return b


@dataclasses.dataclass(frozen=True, slots=True)
class Remove:
    """Remove the item with this key from a list merged with [`merge_by_key`][anymerge.reducers.merge_by_key]."""

    key: typing.Any
    """The key of the item to remove."""


def merge_by_key(key: str | typing.Callable[[typing.Any], typing.Any]) -> ReducerCallable:
    """Create a reducer that merges two lists by matching their items' keys.

    An item replaces the item with the same key in place, an item with a new key is appended,
    and `Remove(key)` deletes the item with that key. Removing a missing key does nothing.

    Args:
        key: The field name to read the key from, or a callable that returns an item's key.

    Returns:
        The reducer.

    Examples:
        >>> Reducer(merge_by_key("id"))
        >>> merge(state, {"todos": [Todo(id=1, done=True), Remove(2)]})
    """

    def get_key(item: typing.Any) -> typing.Any:
        if callable(key):
            return key(item)
        if isinstance(item, dict):
            return item[key]
        return getattr(item, key)

    def reducer(
        a: typing.Iterable[typing.Any], b: typing.Iterable[typing.Any], /
    ) -> list[typing.Any]:
        items = {get_key(item): item for item in a}
        for item in b:
            if isinstance(item, Remove):
                items.pop(item.key, None)
            else:
                items[get_key(item)] = item
        return list(items.values())

    return reducer
