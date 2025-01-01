import typing

import pytest

import anymerge.adapters.dict_adapter as sut
from anymerge.exceptions import AnyMergeTypeError
from tests.adapters import fixtures


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        ({}, True),
        (fixtures.DataclassModel, False),
        (fixtures.TypedDictModel, False),
        (fixtures.PydanticModel, False),
        (fixtures.PydanticV1Model, False),
    ],
)
def test_dict_adapter_is_supported_type(value: typing.Any, expected: bool):
    assert sut.DictAdapter.is_supported_type(value) == expected


def test_dict_adapter_get_fields():
    with pytest.raises(AnyMergeTypeError) as excinfo:
        sut.DictAdapter(typing.cast(typing.Any, {})).get_fields()

    assert (
        str(excinfo.value)
        == "dicts do not support field annotations, please use a TypedDict with DictAdapter instead"
    )
