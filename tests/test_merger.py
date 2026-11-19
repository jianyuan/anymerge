import dataclasses
import operator
import typing

import pydantic
import pytest

import anymerge._merger as sut
from anymerge._api import Reducer
from anymerge.adapters.typeddict_adapter import TypedDictAdapter
from anymerge.models import Overwrite

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
    ],
)
def test_merge(a: typing.Any, b: typing.Any, expected: typing.Any):
    result = sut.merge(a, b)
    assert result == expected


@pytest.mark.parametrize(
    ("a", "expected"),
    [
        pytest.param(DataclassModel4(a=1), DataclassModel4(a=2), id="dataclass"),
        pytest.param(
            TypedDictAdapter(TypedDictModel4).wrap(TypedDictModel4(a=1)),
            TypedDictModel4(a=2),
            id="typeddict",
        ),
        pytest.param(PydanticModel4(a=1), PydanticModel4(a=2), id="pydantic"),
    ],
)
@pytest.mark.parametrize(
    "b",
    [
        pytest.param(DataclassModel4(a=1), id="dataclass"),
        pytest.param(TypedDictAdapter(TypedDictModel4).wrap(TypedDictModel4(a=1)), id="typeddict"),
        pytest.param(PydanticModel4(a=1), id="pydantic"),
    ],
)
def test_merge_mixed(a: typing.Any, b: typing.Any, expected: typing.Any):
    result = sut.merge(a, b)
    assert result == expected


@pytest.mark.parametrize(
    ("a", "expected"),
    [
        pytest.param(DataclassModel4(a=1), DataclassModel4(a=2), id="dataclass"),
        pytest.param(
            TypedDictAdapter(TypedDictModel4).wrap(TypedDictModel4(a=1)),
            TypedDictModel4(a=2),
            id="typeddict",
        ),
        pytest.param(PydanticModel4(a=1), PydanticModel4(a=2), id="pydantic"),
    ],
)
def test_merge_with_dict(a: typing.Any, expected: typing.Any):
    result = sut.merge(a, {"a": 1})
    assert result == expected


class PydanticModel7(pydantic.BaseModel):
    """Pydantic model with a reducer field and a field with a default"""

    a: typing.Annotated[int, Reducer(operator.add)] = 0
    b: str = "default"


def test_merge_ignores_unset_pydantic_fields():
    result = sut.merge(PydanticModel7(a=5, b="kept"), PydanticModel7(a=1))
    assert result == PydanticModel7(a=6, b="kept")


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        pytest.param(
            DataclassModel4(a=1), {"a": Overwrite(0)}, DataclassModel4(a=0), id="dataclass"
        ),
        pytest.param(PydanticModel4(a=1), {"a": Overwrite(0)}, PydanticModel4(a=0), id="pydantic"),
        pytest.param(
            PydanticModel6(a=PydanticModel4(a=1)),
            {"a": Overwrite(PydanticModel4(a=0))},
            PydanticModel6(a=PydanticModel4(a=0)),
            id="deep",
        ),
        pytest.param(
            PydanticModel6(a=PydanticModel4(a=1)),
            {"a": {"a": Overwrite(0)}},
            PydanticModel6(a=PydanticModel4(a=0)),
            id="nested",
        ),
    ],
)
def test_merge_with_overwrite(a: typing.Any, b: typing.Any, expected: typing.Any):
    assert sut.merge(a, b) == expected
