import typing

from anymerge.adapters import ADAPTERS
from anymerge.adapters.base_adapter import WrappedValue
from anymerge.exceptions import AnyMergeTypeError

T = typing.TypeVar("T")


def maybe_adapt_value(value: typing.Any) -> WrappedValue[typing.Any]:
    if isinstance(value, WrappedValue):
        return typing.cast(WrappedValue[typing.Any], value)

    for adapter_cls in ADAPTERS:
        if adapter_cls.is_supported_type(value):
            return adapter_cls(value).wrap(value)

    msg = f"Unsupported instance type: {value}"
    raise AnyMergeTypeError(msg)
