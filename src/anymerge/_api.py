import types
import typing

from anymerge import models
from anymerge.exceptions import AnyMergeValueError
from anymerge.types import ReducerCallable


@typing.overload
def Reducer(reducer: ReducerCallable) -> models.ReducerInfo: ...


@typing.overload
def Reducer(*, deep: typing.Literal[True]) -> models.ReducerInfo: ...


@typing.overload
def Reducer(reducer: types.EllipsisType) -> models.ReducerInfo: ...


def Reducer(  # noqa: N802
    reducer: ReducerCallable | types.EllipsisType | None = None,
    *,
    deep: bool | None = None,
) -> models.ReducerInfo:
    """Create a [`ReducerInfo`][anymerge.models.ReducerInfo] object with the given `reducer` callable or `deep` set to True.

    Args:
        reducer: The reducer callable to apply to the field. If set to `...`, the reducer will be applied deeply.
        deep: Whether to apply the reducer deeply.

    Returns:
        A [`ReducerInfo`][anymerge.models.ReducerInfo] object with the given `reducer` callable or `deep` set to True.

    Examples:
        Define a reducer callable:

            >>> Reducer(operator.add)

        To apply a reducer deeply, either use `...` as the `reducer` argument or set `deep` to `True`:

            >>> Reducer(...)
            >>> Reducer(deep=True)
    """
    if reducer is ...:
        if deep is False:
            msg = "deep cannot be False when reducer is ..."
            raise AnyMergeValueError(msg)
        return models.ReducerInfo(None, deep=True)

    if reducer is None:
        if deep is False:
            msg = "deep cannot be False when reducer is None"
            raise AnyMergeValueError(msg)
        return models.ReducerInfo(None, deep=True)

    if deep is True:
        msg = "deep cannot be True when reducer is provided"
        raise AnyMergeValueError(msg)

    return models.ReducerInfo(reducer=reducer, deep=False)
