from __future__ import annotations

import types
import typing

from anymerge.models import Reducer


def get_base_type(
    annotation: typing.Any,
) -> typing.Any | list[typing.Any]:
    origin = typing.get_origin(annotation)
    if origin is typing.Annotated:
        base_type, *_metadata = typing.get_args(annotation)
        return get_base_type(base_type)

    if origin is typing.Union or origin is types.UnionType:
        return [get_base_type(arg) for arg in typing.get_args(annotation)]

    return annotation


def extract_reducer(
    annotation: typing.Any,
) -> list[Reducer[typing.Any, typing.Any]] | None:
    result: list[Reducer[typing.Any, typing.Any]] = []

    if typing.get_origin(annotation) is typing.Annotated:
        _base_type, *metadata = typing.get_args(annotation)
        result = [data for data in metadata if isinstance(data, Reducer)]

    return result
