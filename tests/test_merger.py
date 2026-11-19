import dataclasses
import operator
import typing

import pydantic
import pytest

import anymerge._merger as sut
from anymerge._api import Reducer
from anymerge.adapters.typeddict_adapter import TypedDictAdapter
from anymerge.exceptions import AnyMergeTypeError, AnyMergeValueError
from anymerge.models import Overwrite
from tests.adapters import future_annotations_fixtures

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


def test_merge_into_model_with_unset_fields():
    assert sut.merge(PydanticModel7(), {"a": 1}) == PydanticModel7(a=1)


@dataclasses.dataclass(slots=True)
class SlotsDataclassModel:
    """Dataclass with slots"""

    a: typing.Annotated[int, Reducer(operator.add)]


def test_merge_slots_dataclass():
    assert sut.merge(SlotsDataclassModel(a=1), {"a": 2}) == SlotsDataclassModel(a=3)


@pytest.mark.parametrize(
    ("a", "expected"),
    [
        pytest.param(
            future_annotations_fixtures.DataclassModel(a=1),
            future_annotations_fixtures.DataclassModel(a=3),
            id="dataclass",
        ),
        pytest.param(
            future_annotations_fixtures.InheritedDataclassModel(a=1),
            future_annotations_fixtures.InheritedDataclassModel(a=3),
            id="inherited",
        ),
    ],
)
def test_merge_string_annotations(a: typing.Any, expected: typing.Any):
    assert sut.merge(a, {"a": 2}) == expected


@pytest.mark.parametrize(
    ("a", "b", "notes"),
    [
        pytest.param(DataclassModel4(a=1), {"a": "x"}, ["while merging field 'a'"], id="flat"),
        pytest.param(
            PydanticModel6(a=PydanticModel4(a=1)),
            {"a": {"a": "x"}},
            ["while merging field 'a'", "while merging field 'a'"],
            id="nested",
        ),
    ],
)
def test_merge_error_names_field(a: typing.Any, b: typing.Any, notes: list[str]):
    with pytest.raises(TypeError) as excinfo:
        sut.merge(a, b)
    assert excinfo.value.__notes__ == notes


@pytest.mark.parametrize(
    ("a", "b", "message"),
    [
        pytest.param(
            DataclassModel4,
            {"a": 1},
            "expected an instance, got the class DataclassModel4",
            id="class-base",
        ),
        pytest.param(
            DataclassModel4(a=1),
            DataclassModel4,
            "expected an instance, got the class DataclassModel4",
            id="class-update",
        ),
        pytest.param(
            DataclassModel4(a=1), 5, "unsupported type int: expected a dataclass", id="unsupported"
        ),
    ],
)
def test_merge_rejects_invalid_values(a: typing.Any, b: typing.Any, message: str):
    with pytest.raises(AnyMergeTypeError, match=message):
        sut.merge(a, b)


class NotRequiredTypedDictModel(typing.TypedDict):
    """TypedDict with a NotRequired reducer field"""

    a: typing.NotRequired[typing.Annotated[list[int], Reducer(operator.add)]]


@pytest.mark.parametrize(
    "value",
    [pytest.param([1], id="plain"), pytest.param(Overwrite([1]), id="overwrite")],
)
def test_merge_into_missing_not_required_key(value: typing.Any):
    base = TypedDictAdapter(NotRequiredTypedDictModel).wrap(NotRequiredTypedDictModel())
    assert sut.merge(base, {"a": value}) == {"a": [1]}


class AliasedPydanticModel(pydantic.BaseModel):
    """Pydantic model with aliased fields"""

    full_name: str = pydantic.Field("", alias="fullName")
    nick_name: str = pydantic.Field("", validation_alias="nickName")
    total: typing.Annotated[int, Reducer(operator.add)] = pydantic.Field(0, alias="Total")


@pytest.mark.parametrize(
    ("b", "expected"),
    [
        pytest.param({"fullName": "x"}, {"full_name": "x"}, id="alias"),
        pytest.param({"full_name": "x"}, {"full_name": "x"}, id="name"),
        pytest.param({"nickName": "x"}, {"nick_name": "x"}, id="validation-alias"),
        pytest.param({"Total": 2}, {"total": 3}, id="alias-with-reducer"),
    ],
)
def test_merge_aliases(b: typing.Any, expected: dict[str, typing.Any]):
    result = sut.merge(AliasedPydanticModel(Total=1), b)
    assert result.model_dump(include=set(expected)) == expected


def test_merge_alias_and_name_conflict():
    with pytest.raises(AnyMergeValueError, match="sets field 'full_name' twice"):
        sut.merge(AliasedPydanticModel(), {"full_name": "x", "fullName": "y"})


class ExtraAllowPydanticModel(pydantic.BaseModel):
    """Pydantic model that allows extra fields"""

    model_config = pydantic.ConfigDict(extra="allow")

    a: int = 0


class ExtraIgnorePydanticModel(pydantic.BaseModel):
    """Pydantic model that ignores extra fields"""

    a: int = 0


@pytest.mark.parametrize(
    ("b", "expected"),
    [
        pytest.param({"x": 2, "y": 3}, {"a": 0, "x": 2, "y": 3}, id="dict"),
        pytest.param(ExtraAllowPydanticModel(x=2, y=3), {"a": 0, "x": 2, "y": 3}, id="model"),
    ],
)
def test_merge_extra_allow(b: typing.Any, expected: dict[str, typing.Any]):
    assert sut.merge(ExtraAllowPydanticModel(x=1), b).model_dump() == expected


def test_merge_extra_allow_default_reducer():
    result = sut.merge(
        ExtraAllowPydanticModel(x=1), {"x": 2}, default_reducer=Reducer(operator.add)
    )
    assert result.model_dump() == {"a": 0, "x": 3}


def test_merge_extra_ignore():
    assert sut.merge(ExtraIgnorePydanticModel(), {"x": 2}).model_dump() == {"a": 0}
