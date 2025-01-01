import operator
import typing

import pytest

import anymerge.adapters.dataclass_adapter as sut
from anymerge.models import FieldInfo, ReducerInfo
from tests.adapters import fixtures


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        ({}, False),
        (fixtures.DataclassModel, True),
        (fixtures.TypedDictModel, False),
        (fixtures.PydanticModel, False),
        (fixtures.PydanticV1Model, False),
    ],
)
def test_dataclass_adapter_is_supported_type(value: typing.Any, expected: bool):
    assert sut.DataclassAdapter.is_supported_type(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            fixtures.DataclassModel1,
            {},
        ),
        (
            fixtures.DataclassModel2,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
            },
        ),
        (
            fixtures.DataclassModel3,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
                "b": FieldInfo(name="b", base_type=str, reducers=None),
            },
        ),
        (
            fixtures.DataclassModel4,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=[ReducerInfo(operator.add)]),
            },
        ),
        (
            fixtures.DataclassModel5,
            {
                "a": FieldInfo(
                    name="a", base_type=fixtures.DataclassModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            fixtures.DataclassModel6,
            {
                "a": FieldInfo(
                    name="a", base_type=fixtures.DataclassModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
    ],
)
def test_dataclass_adapter_get_fields(value: typing.Any, expected: dict[typing.Any, FieldInfo]):
    assert sut.DataclassAdapter(value).get_fields() == expected
