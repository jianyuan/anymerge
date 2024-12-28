import dataclasses
import typing

import pydantic
import pydantic.v1

is_dataclass = dataclasses.is_dataclass
is_typeddict = typing.is_typeddict


def is_pydantic(cls: type[typing.Any]) -> bool:
    return issubclass(cls, pydantic.BaseModel)


def is_pydantic_v1(cls: type[typing.Any]) -> bool:
    return issubclass(cls, pydantic.v1.BaseModel)
