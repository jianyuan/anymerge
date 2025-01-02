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
        (dict[typing.Any, typing.Any], False),
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


@pytest.mark.parametrize(
    ("model", "value", "expected"),
    [
        (
            fixtures.DataclassModel1,
            fixtures.DataclassModel1(),
            {},
        ),
        (
            fixtures.DataclassModel2,
            fixtures.DataclassModel2(a=1),
            {
                "a": 1,
            },
        ),
        (
            fixtures.DataclassModel3,
            fixtures.DataclassModel3(a=1, b="b"),
            {
                "a": 1,
                "b": "b",
            },
        ),
        (
            fixtures.DataclassModel4,
            fixtures.DataclassModel4(a=1),
            {
                "a": 1,
            },
        ),
        (
            fixtures.DataclassModel5,
            fixtures.DataclassModel5(a=fixtures.DataclassModel4(a=1)),
            {
                "a": fixtures.DataclassModel4(a=1),
            },
        ),
        (
            fixtures.DataclassModel6,
            fixtures.DataclassModel6(a=fixtures.DataclassModel4(a=1)),
            {
                "a": fixtures.DataclassModel4(a=1),
            },
        ),
    ],
)
def test_dataclass_adapter_get_values(
    model: typing.Any,
    value: typing.Any,
    expected: dict[typing.Any, typing.Any],
):
    assert sut.DataclassAdapter(model).get_values(value) == expected


def test_dataclass_adapter_copy():
    adapter = sut.DataclassAdapter(fixtures.DataclassModel2)
    value = fixtures.DataclassModel2(a=1)
    changes = {"a": 2}
    copy = adapter.copy(value, changes=changes)

    assert copy == fixtures.DataclassModel2(a=2)
    assert copy is not value
    assert copy is not changes
