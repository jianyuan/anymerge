import typing

import pytest

import anymerge.adapters.typeddict_adapter as sut
from tests.adapters import fixtures


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        (fixtures.DataclassModel, False),
        (fixtures.TypedDictModel, True),
        (fixtures.PydanticModel, False),
        (fixtures.PydanticV1Model, False),
    ],
)
def test_typeddict_adapter_is_supported_type(value: typing.Any, expected: bool):
    assert sut.TypedDictAdapter.is_supported_type(value) == expected
