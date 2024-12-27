from __future__ import annotations

import types
import typing


def get_base_type(
    annotation: typing.Any,
) -> typing.Any | typing.List[typing.Any]:
    origin = typing.get_origin(annotation)
    if origin is typing.Annotated:
        base_type, *_metadata = typing.get_args(annotation)
        return get_base_type(base_type)

    if origin is typing.Union or origin is types.UnionType:
        return [get_base_type(arg) for arg in typing.get_args(annotation)]

    return annotation
