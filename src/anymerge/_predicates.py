from __future__ import annotations

import dataclasses
import typing

import pydantic
import pydantic.v1
import typing_extensions

if typing.TYPE_CHECKING:
    import _typeshed


def is_dataclass(
    cls_or_instance: typing.Any,
) -> typing_extensions.TypeIs[_typeshed.DataclassInstance]:
    return dataclasses.is_dataclass(cls_or_instance)


def is_typeddict(
    cls_or_instance: typing.Any,
) -> typing_extensions.TypeIs[dict[typing.Any, typing.Any]]:
    return typing.is_typeddict(cls_or_instance)


def is_pydantic(
    cls_or_instance: typing.Any,
) -> typing_extensions.TypeIs[pydantic.BaseModel]:
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


def is_pydantic_v1(
    cls_or_instance: typing.Any,
) -> typing_extensions.TypeIs[pydantic.v1.BaseModel]:
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
