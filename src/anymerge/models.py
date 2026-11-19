import dataclasses
import typing

from anymerge.exceptions import AnyMergeValueError
from anymerge.reducers import replace
from anymerge.types import ReducerCallable

T = typing.TypeVar("T")


@dataclasses.dataclass(frozen=True, slots=True)
class ReducerInfo:
    """Information about a reducer to apply to a field."""

    reducer: ReducerCallable | None = None
    """The reducer callable to apply to the field."""

    deep: bool = dataclasses.field(default=False, kw_only=True)
    """Whether to apply the reducer deeply."""

    def __post_init__(self) -> None:
        if self.reducer is not None and self.deep:
            msg = "deep cannot be True when reducer is provided"
            raise AnyMergeValueError(msg)

    def __call__(self, a: typing.Any, b: typing.Any) -> typing.Any:
        if self.reducer is None:
            return b
        return self.reducer(a, b)


DEFAULT_REDUCER = ReducerInfo(replace, deep=False)


@dataclasses.dataclass(frozen=True, slots=True)
class Overwrite(typing.Generic[T]):
    """Wrap a value to replace the field with it, bypassing the field's reducers.

    Examples:
        Reset a field that is annotated with `Reducer(operator.add)`:

            >>> merge(state, {"items": Overwrite([])})
    """

    value: T
    """The value to replace the field with."""


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class FieldInfo:
    """Information about a field in a data model."""

    name: str
    """The name of the field."""

    base_type: type[typing.Any] | list[type[typing.Any]]
    """The base type of the field with annotations removed."""

    reducers: list[ReducerInfo] | None
    """A list of information about reducers to apply to the field."""

    aliases: tuple[str, ...] = ()
    """Other keys an update can use for the field."""
