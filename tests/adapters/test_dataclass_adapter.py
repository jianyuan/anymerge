import typing

import pytest

import anymerge.adapters.dataclass_adapter as sut
from tests.adapters import fixtures


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        (fixtures.DataclassModel, True),
        (fixtures.TypedDictModel, False),
        (fixtures.PydanticModel, False),
        (fixtures.PydanticV1Model, False),
    ],
)
def test_dataclass_adapter_is_supported_type(value: typing.Any, expected: bool):
    assert sut.DataclassAdapter.is_supported_type(value) == expected
