import typing

T = typing.TypeVar("T")


def replace(_a: typing.Any, b: T, /) -> T:
    return b
