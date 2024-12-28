import types
import typing

from anymerge import _models
from anymerge.errors import AnyMergeValueError
from anymerge.types import ReducerCallable


@typing.overload
def Reducer(reducer: ReducerCallable) -> _models.ReducerInfo: ...


@typing.overload
def Reducer(*, deep: typing.Literal[True]) -> _models.ReducerInfo: ...


@typing.overload
def Reducer(reducer: types.EllipsisType) -> _models.ReducerInfo: ...


def Reducer(  # noqa: N802
    reducer: ReducerCallable | types.EllipsisType | None = None,
    *,
    deep: bool | None = None,
) -> _models.ReducerInfo:
    if reducer is ...:
        if deep is False:
            msg = "deep cannot be False when reducer is ..."
            raise AnyMergeValueError(msg)
        return _models.ReducerInfo(None, deep=True)

    if reducer is None:
        if deep is False:
            msg = "deep cannot be False when reducer is None"
            raise AnyMergeValueError(msg)
        return _models.ReducerInfo(None, deep=True)

    if deep is True:
        msg = "deep cannot be True when reducer is provided"
        raise AnyMergeValueError(msg)

    return _models.ReducerInfo(reducer=reducer, deep=False)
