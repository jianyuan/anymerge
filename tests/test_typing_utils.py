import operator
import typing

import pytest
import typing_extensions

import anymerge._typing_utils as sut
from anymerge.models import ReducerInfo


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (None, None),
        (int, int),
        (str, str),
        (list[int], list[int]),
        (dict[str, int], dict[str, int]),
        (typing_extensions.Required[int], int),
        (typing_extensions.NotRequired[int], int),
        (typing.Annotated[int, "metadata"], int),
        (typing.Annotated[list[int], "metadata"], list[int]),
        (typing.Annotated[int | str, "metadata"], [int, str]),
        (typing.Annotated[typing.Union[int | str], "metadata"], [int, str]),  # noqa: UP007
        (typing_extensions.Required[typing.Annotated[int, "metadata"]], int),
        (int | str, [int, str]),
        (typing.Union[int, str], [int, str]),  # noqa: UP007
    ],
)
def test_get_base_type(
    annotation: typing.Any,
    expected: typing.Any | list[typing.Any],
):
    assert sut.get_base_type(annotation) == expected


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (int, None),
        (str, None),
        (None, None),
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
):
    assert sut.extract_reducer(annotation) == expected
