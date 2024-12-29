import typing

ReducerCallable: typing.TypeAlias = typing.Callable[[typing.Any, typing.Any], typing.Any]
"""A reducer that takes two arguments and returns a single value.
"""
