import dataclasses
import typing


class AnyMergeTypeError(TypeError):
    pass


@dataclasses.dataclass(frozen=True, slots=True)
class AnyMergeUnsupportedClassError(AnyMergeTypeError):
    class_: type[typing.Any]
