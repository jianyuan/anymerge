import dataclasses
import operator
import typing

import pydantic
import pydantic.v1
import pytest

import anymerge._merger as sut
from anymerge._api import Reducer
from anymerge.models import ReducerInfo
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


@dataclasses.dataclass
class DataclassModel5:
    """Dataclass with one field with deep reducer"""

    a: typing.Annotated[DataclassModel2, Reducer(...)]


@dataclasses.dataclass
class DataclassModel6:
    """Dataclass with one field with deep reducer"""

    a: typing.Annotated[DataclassModel2, Reducer(deep=True)]


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

    a: typing.Annotated[int, Reducer(operator.add)]  # type: ignore[misc]


class TypedDictModel5(typing.TypedDict):
    """TypedDict with one field with deep reducer"""

    a: typing.Annotated[TypedDictModel2, Reducer(...)]


class TypedDictModel6(typing.TypedDict):
    """TypedDict with one field with deep reducer"""

    a: typing.Annotated[TypedDictModel2, Reducer(deep=True)]


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


class PydanticModel5(pydantic.BaseModel):
    """Pydantic model with one field with deep reducer"""

    a: typing.Annotated[PydanticModel2, Reducer(...)]


class PydanticModel6(pydantic.BaseModel):
    """Pydantic model with one field with deep reducer"""

    a: typing.Annotated[PydanticModel2, Reducer(deep=True)]


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


class PydanticV1Model5(pydantic.v1.BaseModel):
    """Pydantic V1 model with one field with deep reducer"""

    a: typing.Annotated[PydanticV1Model2, Reducer(...)]


class PydanticV1Model6(pydantic.v1.BaseModel):
    """Pydantic V1 model with one field with deep reducer"""

    a: typing.Annotated[PydanticV1Model2, Reducer(deep=True)]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(int, {}, marks=pytest.mark.xfail),
        (DataclassModel1, {}),
        (
            DataclassModel2,
            {
                "a": [ReducerInfo(replace)],
            },
        ),
        (
            DataclassModel3,
            {
                "a": [ReducerInfo(replace)],
                "b": [ReducerInfo(replace)],
            },
        ),
        (
            DataclassModel4,
            {
                "a": [ReducerInfo(operator.add)],
            },
        ),
        (
            DataclassModel5,
            {
                "a": [ReducerInfo(deep=True)],
            },
        ),
        (
            DataclassModel6,
            {
                "a": [ReducerInfo(deep=True)],
            },
        ),
        (
            TypedDictModel1,
            {},
        ),
        (
            TypedDictModel2,
            {
                "a": [ReducerInfo(replace)],
            },
        ),
        (
            TypedDictModel3,
            {
                "a": [ReducerInfo(replace)],
                "b": [ReducerInfo(replace)],
            },
        ),
        (
            TypedDictModel4,
            {
                "a": [ReducerInfo(operator.add)],
            },
        ),
        (
            TypedDictModel5,
            {
                "a": [ReducerInfo(deep=True)],
            },
        ),
        (
            TypedDictModel6,
            {
                "a": [ReducerInfo(deep=True)],
            },
        ),
        (
            PydanticModel1,
            {},
        ),
        (
            PydanticModel2,
            {
                "a": [ReducerInfo(replace)],
            },
        ),
        (
            PydanticModel3,
            {
                "a": [ReducerInfo(replace)],
                "b": [ReducerInfo(replace)],
            },
        ),
        (
            PydanticModel4,
            {
                "a": [ReducerInfo(operator.add)],
            },
        ),
        (
            PydanticModel5,
            {
                "a": [ReducerInfo(deep=True)],
            },
        ),
        (
            PydanticModel6,
            {
                "a": [ReducerInfo(deep=True)],
            },
        ),
        (
            PydanticV1Model1,
            {},
        ),
        (
            PydanticV1Model2,
            {
                "a": [ReducerInfo(replace)],
            },
        ),
        (
            PydanticV1Model3,
            {
                "a": [ReducerInfo(replace)],
                "b": [ReducerInfo(replace)],
            },
        ),
        (
            PydanticV1Model4,
            {
                "a": [ReducerInfo(operator.add)],
            },
        ),
        (
            PydanticV1Model5,
            {
                "a": [ReducerInfo(deep=True)],
            },
        ),
        (
            PydanticV1Model6,
            {
                "a": [ReducerInfo(deep=True)],
            },
        ),
    ],
)
def test_collect_reducers(
    value: typing.Any,
    expected: list[ReducerInfo],
):
    assert sut.collect_reducers(value) == expected
