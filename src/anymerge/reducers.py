import dataclasses
import typing

from anymerge.exceptions import AnyMergeValueError
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

    An item replaces every item with the same key in place, an item with a new key is appended,
    and `Remove(key)` deletes every item with that key. Removing a missing key does nothing.
    If the update repeats a key, the last item with that key wins.

    Args:
        key: The field name to read the key from, or a callable that returns an item's key.

    Raises:
        AnyMergeValueError: An item has no field named `key`.

    Returns:
        The reducer.

    Examples:
        >>> Reducer(merge_by_key("id"))
        >>> merge(state, {"todos": [Todo(id=1, done=True), Remove(2)]})
    """

    def get_key(item: typing.Any) -> typing.Any:
        if callable(key):
            return key(item)
        try:
            return item[key] if isinstance(item, dict) else getattr(item, key)
        except (KeyError, AttributeError) as e:
            msg = f"item has no key {key!r}: {item!r}"
            raise AnyMergeValueError(msg) from e

    def reducer(
        a: typing.Iterable[typing.Any], b: typing.Iterable[typing.Any], /
    ) -> list[typing.Any]:
        # shortcut: linear scan per update item, fine for short lists; index by key if lists get long
        items = [(get_key(item), item) for item in a]
        for item in b:
            if isinstance(item, Remove):
                items = [(k, x) for k, x in items if k != item.key]
                continue
            item_key = get_key(item)
            if any(k == item_key for k, _ in items):
                items = [(k, item if k == item_key else x) for k, x in items]
            else:
                items.append((item_key, item))
        return [x for _, x in items]

    return reducer
