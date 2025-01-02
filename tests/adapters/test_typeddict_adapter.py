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
        (dict[typing.Any, typing.Any], False),
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


@pytest.mark.parametrize(
    ("model", "value", "expected"),
    [
        (
            fixtures.TypedDictModel1,
            fixtures.TypedDictModel1(),
            {},
        ),
        (
            fixtures.TypedDictModel2,
            fixtures.TypedDictModel2(a=1),
            {
                "a": 1,
            },
        ),
        (
            fixtures.TypedDictModel3,
            fixtures.TypedDictModel3(a=1, b="b"),
            {
                "a": 1,
                "b": "b",
            },
        ),
        (
            fixtures.TypedDictModel4,
            fixtures.TypedDictModel4(a=1),
            {
                "a": 1,
            },
        ),
        (
            fixtures.TypedDictModel5,
            fixtures.TypedDictModel5(a=fixtures.TypedDictModel4(a=1)),
            {
                "a": fixtures.TypedDictModel4(a=1),
            },
        ),
        (
            fixtures.TypedDictModel6,
            fixtures.TypedDictModel6(a=fixtures.TypedDictModel4(a=1)),
            {
                "a": fixtures.TypedDictModel4(a=1),
            },
        ),
    ],
)
def test_typeddict_adapter_get_values(
    model: typing.Any,
    value: typing.Any,
    expected: dict[typing.Any, typing.Any],
):
    assert sut.TypedDictAdapter(model).get_values(value) == expected


def test_typeddict_adapter_copy():
    adapter = sut.TypedDictAdapter(fixtures.TypedDictModel2)
    value = fixtures.TypedDictModel2(a=1)
    changes = {"a": 2}
    copy = adapter.copy(value, changes=changes)

    assert copy == fixtures.TypedDictModel2(a=2)
    assert copy is not value
    assert copy is not changes
