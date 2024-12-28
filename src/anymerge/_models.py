import dataclasses
import typing

from anymerge.reducers import replace


@dataclasses.dataclass(frozen=True, slots=True)
class ReducerInfo:
    reducer: typing.Callable[[typing.Any, typing.Any], typing.Any] | None = None
    deep: bool = dataclasses.field(default=False, kw_only=True)


DEFAULT_REDUCER = ReducerInfo(replace, deep=False)
