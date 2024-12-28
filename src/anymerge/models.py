import dataclasses

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


DEFAULT_REDUCER = ReducerInfo(replace, deep=False)
