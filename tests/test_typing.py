"""Static type checks for the public API, verified by running mypy over the tests."""

import dataclasses
import operator
import typing

import pydantic

from anymerge import Reducer, merge, reduce
from anymerge.adapters import TypedDictAdapter


@dataclasses.dataclass
class DataclassModel:
    a: typing.Annotated[int, Reducer(operator.add)] = 0


class PydanticModel(pydantic.BaseModel):
    a: typing.Annotated[int, Reducer(operator.add)] = 0


class TypedDictModel(typing.TypedDict):
    a: typing.Annotated[int, Reducer(operator.add)]


def test_merge_return_types() -> None:
    typing.assert_type(merge(DataclassModel(), {"a": 1}), DataclassModel)
    typing.assert_type(merge(PydanticModel(), {"a": 1}), PydanticModel)
    wrapped = TypedDictAdapter(TypedDictModel).wrap(TypedDictModel(a=0))
    typing.assert_type(merge(wrapped, {"a": 1}), TypedDictModel)


def test_reduce_return_types() -> None:
    typing.assert_type(reduce(DataclassModel(), [{"a": 1}]), DataclassModel)
    typing.assert_type(reduce(PydanticModel(), [{"a": 1}]), PydanticModel)
    wrapped = TypedDictAdapter(TypedDictModel).wrap(TypedDictModel(a=0))
    typing.assert_type(reduce(wrapped, [{"a": 1}]), TypedDictModel)
