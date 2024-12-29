import dataclasses
import typing

import pydantic
import pydantic.v1


@dataclasses.dataclass
class DataclassModel:
    pass


class TypedDictModel(typing.TypedDict):
    pass


class PydanticModel(pydantic.BaseModel):
    pass


class PydanticV1Model(pydantic.v1.BaseModel):
    pass
