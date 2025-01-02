import operator
import typing

import pytest

import anymerge.adapters.pydantic_adapter as sut
from anymerge.models import FieldInfo, ReducerInfo
from tests.adapters import fixtures


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        ({}, False),
        (dict[typing.Any, typing.Any], False),
        (fixtures.DataclassModel, False),
        (fixtures.TypedDictModel, False),
        (fixtures.PydanticModel, True),
        (fixtures.PydanticV1Model, True),
    ],
)
def test_pydantic_adapter_is_supported_type(value: typing.Any, expected: bool):
    assert sut.PydanticAdapter.is_supported_type(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            fixtures.PydanticModel1,
            {},
        ),
        (
            fixtures.PydanticModel2,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
            },
        ),
        (
            fixtures.PydanticModel3,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
                "b": FieldInfo(name="b", base_type=str, reducers=None),
            },
        ),
        (
            fixtures.PydanticModel4,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=[ReducerInfo(operator.add)]),
            },
        ),
        (
            fixtures.PydanticModel5,
            {
                "a": FieldInfo(
                    name="a", base_type=fixtures.PydanticModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            fixtures.PydanticModel6,
            {
                "a": FieldInfo(
                    name="a", base_type=fixtures.PydanticModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            fixtures.PydanticV1Model1,
            {},
        ),
        (
            fixtures.PydanticV1Model2,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
            },
        ),
        (
            fixtures.PydanticV1Model3,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
                "b": FieldInfo(name="b", base_type=str, reducers=None),
            },
        ),
        (
            fixtures.PydanticV1Model4,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=[ReducerInfo(operator.add)]),
            },
        ),
        (
            fixtures.PydanticV1Model5,
            {
                "a": FieldInfo(
                    name="a", base_type=fixtures.PydanticV1Model4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            fixtures.PydanticV1Model6,
            {
                "a": FieldInfo(
                    name="a", base_type=fixtures.PydanticV1Model4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
    ],
)
def test_pydantic_adapter_get_fields(value: typing.Any, expected: dict[typing.Any, FieldInfo]):
    assert sut.PydanticAdapter(value).get_fields() == expected


@pytest.mark.parametrize(
    ("model", "value", "expected"),
    [
        (
            fixtures.PydanticModel1,
            fixtures.PydanticModel1(),
            {},
        ),
        (
            fixtures.PydanticModel2,
            fixtures.PydanticModel2(a=1),
            {
                "a": 1,
            },
        ),
        (
            fixtures.PydanticModel3,
            fixtures.PydanticModel3(a=1, b="b"),
            {
                "a": 1,
                "b": "b",
            },
        ),
        (
            fixtures.PydanticModel4,
            fixtures.PydanticModel4(a=1),
            {
                "a": 1,
            },
        ),
        (
            fixtures.PydanticModel5,
            fixtures.PydanticModel5(a=fixtures.PydanticModel4(a=1)),
            {
                "a": fixtures.PydanticModel4(a=1),
            },
        ),
        (
            fixtures.PydanticModel6,
            fixtures.PydanticModel6(a=fixtures.PydanticModel4(a=1)),
            {
                "a": fixtures.PydanticModel4(a=1),
            },
        ),
        (
            fixtures.PydanticV1Model1,
            fixtures.PydanticV1Model1(),
            {},
        ),
        (
            fixtures.PydanticV1Model2,
            fixtures.PydanticV1Model2(a=1),
            {
                "a": 1,
            },
        ),
        (
            fixtures.PydanticV1Model3,
            fixtures.PydanticV1Model3(a=1, b="b"),
            {
                "a": 1,
                "b": "b",
            },
        ),
        (
            fixtures.PydanticV1Model4,
            fixtures.PydanticV1Model4(a=1),
            {
                "a": 1,
            },
        ),
        (
            fixtures.PydanticV1Model5,
            fixtures.PydanticV1Model5(a=fixtures.PydanticV1Model4(a=1)),
            {
                "a": fixtures.PydanticV1Model4(a=1),
            },
        ),
        (
            fixtures.PydanticV1Model6,
            fixtures.PydanticV1Model6(a=fixtures.PydanticV1Model4(a=1)),
            {
                "a": fixtures.PydanticV1Model4(a=1),
            },
        ),
    ],
)
def test_pydantic_adapter_get_values(
    model: typing.Any,
    value: typing.Any,
    expected: dict[typing.Any, typing.Any],
):
    assert sut.PydanticAdapter(model).get_values(value) == expected


@pytest.mark.parametrize(
    ("model", "value", "expected"),
    [
        (fixtures.PydanticModel2, fixtures.PydanticModel2(a=1), fixtures.PydanticModel2(a=2)),
        (fixtures.PydanticV1Model2, fixtures.PydanticV1Model2(a=1), fixtures.PydanticV1Model2(a=2)),
    ],
)
def test_pydantic_adapter_copy(
    model: typing.Any,
    value: typing.Any,
    expected: typing.Any,
):
    adapter = sut.PydanticAdapter(model)
    changes = {"a": 2}
    copy = adapter.copy(value, changes=changes)

    assert copy == expected
    assert copy is not value
    assert copy is not changes
