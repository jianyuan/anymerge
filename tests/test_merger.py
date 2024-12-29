import dataclasses
import operator
import typing

import pydantic
import pydantic.v1
import pytest

import anymerge._merger as sut
from anymerge._api import Reducer
from anymerge.models import FieldInfo, ReducerInfo

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

    a: typing.Annotated[DataclassModel4, Reducer(...)]


@dataclasses.dataclass
class DataclassModel6:
    """Dataclass with one field with deep reducer"""

    a: typing.Annotated[DataclassModel4, Reducer(deep=True)]


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

    a: typing.Annotated[TypedDictModel4, Reducer(...)]


class TypedDictModel6(typing.TypedDict):
    """TypedDict with one field with deep reducer"""

    a: typing.Annotated[TypedDictModel4, Reducer(deep=True)]


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

    a: typing.Annotated[PydanticModel4, Reducer(...)]


class PydanticModel6(pydantic.BaseModel):
    """Pydantic model with one field with deep reducer"""

    a: typing.Annotated[PydanticModel4, Reducer(deep=True)]


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

    a: typing.Annotated[PydanticV1Model4, Reducer(...)]


class PydanticV1Model6(pydantic.v1.BaseModel):
    """Pydantic V1 model with one field with deep reducer"""

    a: typing.Annotated[PydanticV1Model4, Reducer(deep=True)]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(int, {}, marks=pytest.mark.xfail),
        (DataclassModel1, {}),
        (
            DataclassModel2,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
            },
        ),
        (
            DataclassModel3,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
                "b": FieldInfo(name="b", base_type=str, reducers=None),
            },
        ),
        (
            DataclassModel4,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=[ReducerInfo(operator.add)]),
            },
        ),
        (
            DataclassModel5,
            {
                "a": FieldInfo(
                    name="a", base_type=DataclassModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            DataclassModel6,
            {
                "a": FieldInfo(
                    name="a", base_type=DataclassModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            TypedDictModel1,
            {},
        ),
        (
            TypedDictModel2,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
            },
        ),
        (
            TypedDictModel3,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
                "b": FieldInfo(name="b", base_type=str, reducers=None),
            },
        ),
        (
            TypedDictModel4,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=[ReducerInfo(operator.add)]),
            },
        ),
        (
            TypedDictModel5,
            {
                "a": FieldInfo(
                    name="a", base_type=TypedDictModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            TypedDictModel6,
            {
                "a": FieldInfo(
                    name="a", base_type=TypedDictModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            PydanticModel1,
            {},
        ),
        (
            PydanticModel2,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
            },
        ),
        (
            PydanticModel3,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
                "b": FieldInfo(name="b", base_type=str, reducers=None),
            },
        ),
        (
            PydanticModel4,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=[ReducerInfo(operator.add)]),
            },
        ),
        (
            PydanticModel5,
            {
                "a": FieldInfo(
                    name="a", base_type=PydanticModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            PydanticModel6,
            {
                "a": FieldInfo(
                    name="a", base_type=PydanticModel4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            PydanticV1Model1,
            {},
        ),
        (
            PydanticV1Model2,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
            },
        ),
        (
            PydanticV1Model3,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=None),
                "b": FieldInfo(name="b", base_type=str, reducers=None),
            },
        ),
        (
            PydanticV1Model4,
            {
                "a": FieldInfo(name="a", base_type=int, reducers=[ReducerInfo(operator.add)]),
            },
        ),
        (
            PydanticV1Model5,
            {
                "a": FieldInfo(
                    name="a", base_type=PydanticV1Model4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
        (
            PydanticV1Model6,
            {
                "a": FieldInfo(
                    name="a", base_type=PydanticV1Model4, reducers=[ReducerInfo(deep=True)]
                ),
            },
        ),
    ],
)
def test_collect_fields(
    value: typing.Any,
    expected: dict[str, FieldInfo],
):
    assert sut.collect_fields(value) == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (DataclassModel2(a=1), DataclassModel2(a=2), DataclassModel2(a=2)),
        (DataclassModel3(a=1, b="a"), DataclassModel3(a=2, b="b"), DataclassModel3(a=2, b="b")),
        (DataclassModel4(a=1), DataclassModel4(a=1), DataclassModel4(a=2)),
        (
            DataclassModel6(a=DataclassModel4(a=1)),
            DataclassModel6(a=DataclassModel4(a=1)),
            DataclassModel6(a=DataclassModel4(a=2)),
        ),
        (PydanticModel2(a=1), PydanticModel2(a=2), PydanticModel2(a=2)),
        (PydanticModel3(a=1, b="a"), PydanticModel3(a=2, b="b"), PydanticModel3(a=2, b="b")),
        (PydanticModel4(a=1), PydanticModel4(a=1), PydanticModel4(a=2)),
        (
            PydanticModel6(a=PydanticModel4(a=1)),
            PydanticModel6(a=PydanticModel4(a=1)),
            PydanticModel6(a=PydanticModel4(a=2)),
        ),
        (PydanticV1Model2(a=1), PydanticV1Model2(a=2), PydanticV1Model2(a=2)),
        (
            PydanticV1Model3(a=1, b="a"),
            PydanticV1Model3(a=2, b="b"),
            PydanticV1Model3(a=2, b="b"),
        ),
        (PydanticV1Model4(a=1), PydanticV1Model4(a=1), PydanticV1Model4(a=2)),
        (
            PydanticV1Model6(a=PydanticV1Model4(a=1)),
            PydanticV1Model6(a=PydanticV1Model4(a=1)),
            PydanticV1Model6(a=PydanticV1Model4(a=2)),
        ),
    ],
)
def test_merge(a: typing.Any, b: typing.Any, expected: typing.Any):
    result = sut.merge(a, b)
    assert result == expected


@pytest.mark.parametrize(
    "a",
    [
        pytest.param(DataclassModel4(a=1), id="dataclass"),
        pytest.param(PydanticModel4(a=1), id="pydantic"),
        pytest.param(PydanticV1Model4(a=1), id="pydantic_v1"),
    ],
)
@pytest.mark.parametrize(
    "b",
    [
        pytest.param(DataclassModel4(a=1), id="dataclass"),
        pytest.param(PydanticModel4(a=1), id="pydantic"),
        pytest.param(PydanticV1Model4(a=1), id="pydantic_v1"),
    ],
)
def test_merge_mixed(a: typing.Any, b: typing.Any):
    cls = type(a)  # type: ignore
    result = sut.merge(a, b)
    assert result == cls(a=2)
