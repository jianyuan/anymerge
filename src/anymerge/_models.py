import dataclasses
import typing

P = typing.ParamSpec("P")
R = typing.TypeVar("R")


@dataclasses.dataclass(frozen=True)
class Reducer(typing.Generic[P, R]):
    reducer: typing.Callable[P, R]
