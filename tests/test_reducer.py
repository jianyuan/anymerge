import typing

import pytest

import anymerge._reducer as sut
from anymerge.adapters import TypedDictAdapter
from tests.adapters import fixtures


def test_reduce():
    assert sut.reduce(
        fixtures.PydanticModel4(a=0),
        [
            fixtures.DataclassModel2(a=1),
            fixtures.PydanticModel2(a=2),
            fixtures.TypedDictModel2(a=3),
        ],
    ) == fixtures.PydanticModel4(a=6)


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        pytest.param([], {"a": 0}, id="no-updates"),
        pytest.param([{"a": 1}], {"a": 1}, id="one-update"),
        pytest.param([{"a": 1}, {"a": 2}, {"a": 3}], {"a": 6}, id="many-updates"),
    ],
)
def test_reduce_wrapped_typeddict(updates: list[typing.Any], expected: typing.Any):
    initial = TypedDictAdapter(fixtures.TypedDictModel4).wrap(fixtures.TypedDictModel4(a=0))
    result = sut.reduce(initial, updates)
    assert result == expected
    assert type(result) is dict
