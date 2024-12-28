import dataclasses
import typing

import pydantic
import pydantic.v1


def is_dataclass(cls_or_instance: typing.Any) -> bool:
    return dataclasses.is_dataclass(cls_or_instance)


def is_typeddict(cls_or_instance: typing.Any) -> bool:
    return typing.is_typeddict(cls_or_instance)


def is_pydantic(cls_or_instance: typing.Any) -> bool:
    return isinstance(
        cls_or_instance,
        pydantic.BaseModel,
    ) or (
        isinstance(cls_or_instance, type)
        and issubclass(
            cls_or_instance,
            pydantic.BaseModel,
        )
    )


def is_pydantic_v1(cls_or_instance: typing.Any) -> bool:
    return isinstance(
        cls_or_instance,
        pydantic.v1.BaseModel,
    ) or (
        isinstance(cls_or_instance, type)
        and issubclass(
            cls_or_instance,
            pydantic.v1.BaseModel,
        )
    )
