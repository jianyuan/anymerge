import dataclasses
import typing

from anymerge.reducers import replace

P = typing.ParamSpec("P")
R = typing.TypeVar("R")


@dataclasses.dataclass(frozen=True, slots=True)
class Reducer(typing.Generic[P, R]):
    reducer: typing.Callable[P, R]


DEFAULT_REDUCER = Reducer(replace)
