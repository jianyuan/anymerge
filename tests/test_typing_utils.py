import typing

import pytest

import anymerge._typing_utils as sut


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (int, int),
        (str, str),
        (typing.List[int], typing.List[int]),
        (typing.Dict[str, int], typing.Dict[str, int]),
        (typing.Annotated[int, "metadata"], int),
        (typing.Annotated[typing.List[int], "metadata"], typing.List[int]),
        (typing.Annotated[typing.Union[int, str], "metadata"], [int, str]),
        (typing.Annotated[int | str, "metadata"], [int, str]),
        (typing.Union[int, str], [int, str]),
        (int | str, [int, str]),
    ],
)
def test_get_base_type(
    annotation: typing.Any,
    expected: typing.Any | typing.List[typing.Any],
) -> None:
    assert sut.get_base_type(annotation) == expected
