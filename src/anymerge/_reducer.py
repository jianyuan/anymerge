import typing

from anymerge._merger import merge
from anymerge.adapters.base_adapter import WrappedValue
from anymerge.models import DEFAULT_REDUCER, ReducerInfo

T = typing.TypeVar("T")


@typing.overload
def reduce(
    initial: WrappedValue[T],
    iterable: typing.Iterable[typing.Any],
    *,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> T: ...


@typing.overload
def reduce(
    initial: T,
    iterable: typing.Iterable[typing.Any],
    *,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> T: ...


def reduce(
    initial: typing.Any,
    iterable: typing.Iterable[typing.Any],
    *,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> typing.Any:
    """Reduce an iterable of instances of data models.

    Args:
        initial: The initial instance to reduce. This should contain all the annotations with the reducer information.
        iterable: The iterable of instances to reduce.

    Returns:
        The reduced instance.
    """
    value = initial
    for item in iterable:
        value = merge(value, item, default_reducer=default_reducer)
        if isinstance(initial, WrappedValue):
            # merge returns a plain dict for a wrapped TypedDict, so wrap it again for the next update
            value = initial.adapter.wrap(value)
    return value.unwrap() if isinstance(value, WrappedValue) else value
