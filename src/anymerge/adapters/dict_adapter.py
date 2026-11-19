import typing

from anymerge._typing_utils import lenient_isinstance
from anymerge.adapters.base_adapter import BaseAdapter
from anymerge.exceptions import AnyMergeTypeError
from anymerge.models import FieldInfo

T = typing.TypeVar("T", bound=dict[typing.Any, typing.Any])


class DictAdapter(BaseAdapter[T], typing.Generic[T]):
    @classmethod
    def is_supported_type(cls, value: typing.Any) -> typing.TypeGuard[type[T]]:
        return not typing.is_typeddict(value) and (
            lenient_isinstance(value, dict) or typing.get_origin(value) is dict
        )

    def get_fields(self) -> dict[typing.Any, FieldInfo]:
        msg = (
            "a plain dict has no field annotations, so it can't be the base of a merge; "
            "declare a TypedDict and wrap the base with TypedDictAdapter(Model).wrap(value)"
        )
        raise AnyMergeTypeError(msg)

    def get_values(self, value: T) -> dict[typing.Any, typing.Any]:
        return dict(value)

    def copy(self, value: T, *, changes: dict[typing.Any, typing.Any]) -> T:
        return typing.cast("T", {**value, **changes})
