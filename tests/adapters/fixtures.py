import dataclasses
import operator
import typing

import pydantic
import pydantic.v1

from anymerge._api import Reducer


@dataclasses.dataclass
class DataclassModel:
    pass


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


class TypedDictModel(typing.TypedDict):
    pass


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


class PydanticModel(pydantic.BaseModel):
    pass


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


class PydanticV1Model(pydantic.v1.BaseModel):
    pass


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
