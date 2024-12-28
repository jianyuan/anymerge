import operator
import typing

import pytest

import anymerge._typing_utils as sut
from anymerge._models import ReducerInfo


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (None, None),
        (int, int),
        (str, str),
        (list[int], list[int]),
        (dict[str, int], dict[str, int]),
        (typing.Annotated[int, "metadata"], int),
        (typing.Annotated[list[int], "metadata"], list[int]),
        (typing.Annotated[int | str, "metadata"], [int, str]),
        (typing.Annotated[typing.Union[int | str], "metadata"], [int, str]),  # noqa: UP007
        (int | str, [int, str]),
        (typing.Union[int, str], [int, str]),  # noqa: UP007
    ],
)
def test_get_base_type(
    annotation: typing.Any,
    expected: typing.Any | list[typing.Any],
) -> None:
    assert sut.get_base_type(annotation) == expected


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (int, []),
        (str, []),
        (None, []),
        (typing.Annotated[int, ReducerInfo(operator.add)], [ReducerInfo(operator.add)]),
        (
            typing.Annotated[int, ReducerInfo(operator.add), ReducerInfo(operator.mul)],
            [ReducerInfo(operator.add), ReducerInfo(operator.mul)],
        ),
    ],
)
def test_extract_reducer(
    annotation: typing.Any,
    expected: typing.Any | None,
) -> None:
    assert sut.extract_reducer(annotation) == expected
