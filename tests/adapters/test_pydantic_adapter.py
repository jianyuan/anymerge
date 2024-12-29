import typing

import pytest

import anymerge.adapters.pydantic_adapter as sut
from tests.adapters import fixtures


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        (fixtures.DataclassModel, False),
        (fixtures.TypedDictModel, False),
        (fixtures.PydanticModel, True),
        (fixtures.PydanticV1Model, True),
    ],
)
def test_pydantic_adapter_is_supported_type(value: typing.Any, expected: bool):
    assert sut.PydanticAdapter.is_supported_type(value) == expected
