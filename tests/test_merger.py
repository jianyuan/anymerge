import dataclasses
import operator
import typing

import pydantic
import pydantic.v1
import pytest

import anymerge._merger as sut
from anymerge.models import Reducer
from anymerge.reducers import replace

# Dataclasses


@dataclasses.dataclass
class DataclassModel1:
    """Bare dataclass"""


@dataclasses.dataclass
class DataclassModel2:
    """Dataclass with one field"""

    a: int


@dataclasses.dataclass
class DataclassModel3(DataclassModel2):
    """Dataclass with two fields, one inherited"""

    b: str


@dataclasses.dataclass
class DataclassModel4(DataclassModel2):
    """Dataclass with one overridden field"""

    a: typing.Annotated[int, Reducer(operator.add)]


# TypedDicts


class TypedDictModel1(typing.TypedDict):
    """Bare TypedDict"""


class TypedDictModel2(TypedDictModel1):
    """TypedDict with one field"""

    a: int


class TypedDictModel3(TypedDictModel2):
    """TypedDict with two fields, one inherited"""

    b: str


class TypedDictModel4(TypedDictModel2):
    """TypedDict with one overridden field"""

    a: typing.Annotated[int, Reducer(operator.add)]


# Pydantic models


class PydanticModel1(pydantic.BaseModel):
    """Bare Pydantic model"""


class PydanticModel2(PydanticModel1):
    """Pydantic model with one field"""

    a: int


class PydanticModel3(PydanticModel2):
    """Pydantic model with two fields, one inherited"""

    b: str


class PydanticModel4(PydanticModel2):
    """Pydantic model with one overridden field"""

    a: typing.Annotated[int, Reducer(operator.add)]


# Pydantic V1 models


class PydanticV1Model1(pydantic.v1.BaseModel):
    """Bare Pydantic V1 model"""


class PydanticV1Model2(PydanticV1Model1):
    """Pydantic V1 model with one field"""

    a: int


class PydanticV1Model3(PydanticV1Model2):
    """Pydantic V1 model with two fields, one inherited"""

    b: str


class PydanticV1Model4(PydanticV1Model2):
    """Pydantic V1 model with one overridden field"""

    a: typing.Annotated[int, Reducer(operator.add)]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(int, {}, marks=pytest.mark.xfail),
        (DataclassModel1, {}),
        (
            DataclassModel2,
            {
                "a": [Reducer(replace)],
            },
        ),
        (
            DataclassModel3,
            {
                "a": [Reducer(replace)],
                "b": [Reducer(replace)],
            },
        ),
        (
            DataclassModel4,
            {
                "a": [Reducer(operator.add)],
            },
        ),
        (
            TypedDictModel1,
            {},
        ),
        (
            TypedDictModel2,
            {
                "a": [Reducer(replace)],
            },
        ),
        (
            TypedDictModel3,
            {
                "a": [Reducer(replace)],
                "b": [Reducer(replace)],
            },
        ),
        (
            TypedDictModel4,
            {
                "a": [Reducer(operator.add)],
            },
        ),
        (
            PydanticModel1,
            {},
        ),
        (
            PydanticModel2,
            {
                "a": [Reducer(replace)],
            },
        ),
        (
            PydanticModel3,
            {
                "a": [Reducer(replace)],
                "b": [Reducer(replace)],
            },
        ),
        (
            PydanticModel4,
            {
                "a": [Reducer(operator.add)],
            },
        ),
        (
            PydanticV1Model1,
            {},
        ),
        (
            PydanticV1Model2,
            {
                "a": [Reducer(replace)],
            },
        ),
        (
            PydanticV1Model3,
            {
                "a": [Reducer(replace)],
                "b": [Reducer(replace)],
            },
        ),
        (
            PydanticV1Model4,
            {
                "a": [Reducer(operator.add)],
            },
        ),
    ],
)
def test_collect_reducers(
    value: typing.Any,
    expected: list[Reducer[typing.Any, typing.Any]],
):
    assert sut.collect_reducers(value) == expected
