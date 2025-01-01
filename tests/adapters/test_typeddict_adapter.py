import operator
import typing

import pytest

import anymerge.adapters.typeddict_adapter as sut
from anymerge.models import FieldInfo, ReducerInfo
from tests.adapters import fixtures


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        ({}, False),
        (fixtures.DataclassModel, False),
        (fixtures.TypedDictModel, True),
        (fixtures.PydanticModel, False),
        (fixtures.PydanticV1Model, False),
    ],
)
def test_typeddict_adapter_is_supported_type(value: typing.Any, expected: bool):
    assert sut.TypedDictAdapter.is_supported_type(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            fixtures.TypedDictModel1,
            {},
        ),
        (
            fixtures.TypedDictModel2,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
            },
        ),
        (
            fixtures.TypedDictModel3,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
                "b": FieldInfo(name="b", base_type=str, reducers=None),
            },
        ),
        (
            fixtures.TypedDictModel4,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=[ReducerInfo(operator.add)]),
            },
        ),
        (
            fixtures.TypedDictModel5,
            {
                "a": FieldInfo(
                    name="a", base_type=fixtures.TypedDictModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            fixtures.TypedDictModel6,
            {
                "a": FieldInfo(
                    name="a", base_type=fixtures.TypedDictModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
    ],
)
def test_typeddict_adapter_get_fields(value: typing.Any, expected: dict[typing.Any, FieldInfo]):
    assert sut.TypedDictAdapter(value).get_fields() == expected
