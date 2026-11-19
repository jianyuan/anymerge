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
        (dict[typing.Any, typing.Any], True),
        (fixtures.DataclassModel, False),
        (fixtures.TypedDictModel, False),
        (fixtures.PydanticModel, False),
    ],
)
def test_dict_adapter_is_supported_type(value: typing.Any, expected: bool):
    assert sut.DictAdapter.is_supported_type(value) == expected


def test_dict_adapter_get_fields():
    with pytest.raises(AnyMergeTypeError) as excinfo:
        sut.DictAdapter(dict[typing.Any, typing.Any]).get_fields()

    assert (
        str(excinfo.value)
        == "a plain dict has no field annotations, so it can't be the base of a merge; "
        "declare a TypedDict and wrap the base with TypedDictAdapter(Model).wrap(value)"
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            {},
            {},
        ),
        (
            {
                "a": 1,
            },
            {
                "a": 1,
            },
        ),
        (
            {
                "a": 1,
                "b": "b",
            },
            {
                "a": 1,
                "b": "b",
            },
        ),
        (
            {
                "a": fixtures.DataclassModel4(a=1),
            },
            {
                "a": fixtures.DataclassModel4(a=1),
            },
        ),
    ],
)
def test_dict_adapter_get_values(
    value: typing.Any,
    expected: dict[typing.Any, typing.Any],
):
    assert sut.DictAdapter(dict[typing.Any, typing.Any]).get_values(value) == expected


def test_dict_adapter_copy():
    adapter = sut.DictAdapter(dict[typing.Any, typing.Any])
    value = {"a": 1}
    changes = {"a": 2}
    copy = adapter.copy(value, changes=changes)

    assert copy == {"a": 2}
    assert copy is not value
    assert copy is not changes
