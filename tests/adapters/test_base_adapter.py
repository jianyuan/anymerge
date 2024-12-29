import typing

import anymerge.adapters.base_adapter as sut
from anymerge.models import FieldInfo

T = typing.TypeVar("T")


def test_base_adapter_model():
    class Adapter(sut.BaseAdapter[T]):
        @classmethod
        def is_supported_type(cls, value: typing.Any) -> typing.TypeGuard[type[T]]:
            return True

        def get_fields(self) -> dict[typing.Any, FieldInfo]:
            return {}

        def get_values(self, value: T) -> dict[typing.Any, typing.Any]:
            return {}

        def copy(self, value: T, *, changes: dict[typing.Any, typing.Any]) -> T:
            return value

    class Model:
        pass

    assert Adapter(Model).model is Model
