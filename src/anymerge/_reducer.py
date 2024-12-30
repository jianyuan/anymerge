import typing

from anymerge._merger import merge
from anymerge.models import DEFAULT_REDUCER, ReducerInfo

T = typing.TypeVar("T")


def reduce(
    initial: T,
    iterable: typing.Iterable[typing.Any],
    *,
    default_reducer: ReducerInfo = DEFAULT_REDUCER,
) -> T:
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
    return value
