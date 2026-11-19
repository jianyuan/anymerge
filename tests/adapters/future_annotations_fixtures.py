"""Fixtures declared with postponed evaluation of annotations, so their annotations are strings."""

from __future__ import annotations

import dataclasses
import operator
import typing

from anymerge import Reducer


@dataclasses.dataclass
class DataclassModel:
    """Dataclass with string annotations"""

    a: typing.Annotated[int, Reducer(operator.add)]


@dataclasses.dataclass
class InheritedDataclassModel(DataclassModel):
    """Dataclass inheriting a string-annotated reducer field"""

    b: str = "b"


@dataclasses.dataclass
class UnresolvableDataclassModel:
    """Dataclass with an annotation that names an undefined type"""

    a: UndefinedType  # type: ignore[name-defined]  # noqa: F821
