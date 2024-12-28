import dataclasses
import typing

from anymerge.exceptions import AnyMergeValueError
from anymerge.reducers import replace
from anymerge.types import ReducerCallable


@dataclasses.dataclass(frozen=True, slots=True)
class ReducerInfo:
    reducer: ReducerCallable | None = None
    deep: bool = dataclasses.field(default=False, kw_only=True)

    def __post_init__(self) -> None:
        if self.reducer is not None and self.deep:
            msg = "deep cannot be True when reducer is provided"
            raise AnyMergeValueError(msg)

    def __call__(self, a: typing.Any, b: typing.Any) -> typing.Any:
        if self.reducer is None:
            return b
        return self.reducer(a, b)


DEFAULT_REDUCER = ReducerInfo(replace, deep=False)


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class FieldInfo:
    name: str
    base_type: type[typing.Any] | list[type[typing.Any]]
    reducers: list[ReducerInfo] | None
