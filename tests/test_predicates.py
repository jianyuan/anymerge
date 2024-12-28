import dataclasses
import typing

import pydantic
import pydantic.v1
import pytest

import anymerge._predicates as sut


@dataclasses.dataclass
class DataclassModel:
    pass


class TypedDictModel(typing.TypedDict):
    pass


class PydanticModel(pydantic.BaseModel):
    pass


class PydanticV1Model(pydantic.v1.BaseModel):
    pass


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        (DataclassModel, True),
        (DataclassModel(), True),
        (TypedDictModel, False),
        (TypedDictModel(), False),
        (PydanticModel, False),
        (PydanticModel(), False),
        (PydanticV1Model, False),
        (PydanticV1Model(), False),
    ],
)
def test_is_dataclass(value: typing.Any, expected: bool):
    assert sut.is_dataclass(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        (DataclassModel, False),
        (DataclassModel(), False),
        (TypedDictModel, True),
        (TypedDictModel(), False),
        (PydanticModel, False),
        (PydanticModel(), False),
        (PydanticV1Model, False),
        (PydanticV1Model(), False),
    ],
)
def test_is_typeddict(value: typing.Any, expected: bool):
    assert sut.is_typeddict(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        (DataclassModel, False),
        (DataclassModel(), False),
        (TypedDictModel, False),
        (TypedDictModel(), False),
        (PydanticModel, True),
        (PydanticModel(), True),
        (PydanticV1Model, False),
        (PydanticV1Model(), False),
    ],
)
def test_is_pydantic(value: typing.Any, expected: bool):
    assert sut.is_pydantic(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (1, False),
        (DataclassModel, False),
        (DataclassModel(), False),
        (TypedDictModel, False),
        (TypedDictModel(), False),
        (PydanticModel, False),
        (PydanticModel(), False),
        (PydanticV1Model, True),
        (PydanticV1Model(), True),
    ],
)
def test_is_pydantic_v1(value: typing.Any, expected: bool):
    assert sut.is_pydantic_v1(value) is expected
