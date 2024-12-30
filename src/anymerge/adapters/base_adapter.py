from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from anymerge.models import FieldInfo

T = typing.TypeVar("T")


class BaseAdapter(abc.ABC, typing.Generic[T]):
    model: type[T]
    """The model type of the adapter."""

    def __init__(self, model: type[T]) -> None:
        self.model = model

    @classmethod
    @abc.abstractmethod
    def is_supported_type(cls, value: typing.Any) -> typing.TypeGuard[type[T]]:
        """Check if the value is supported by the adapter.

        Args:
            value: The value to check.

        Returns:
            Whether the value is supported by the adapter.
        """

    @abc.abstractmethod
    def get_fields(self) -> dict[typing.Any, FieldInfo]:
        """Get the fields of the model.

        Returns:
            The fields of the model.
        """

    @abc.abstractmethod
    def get_values(self, value: T) -> dict[typing.Any, typing.Any]:
        """Get the values of the instance.

        Args:
            value: The instance to get the values from.

        Returns:
            The values of the instance.
        """

    @abc.abstractmethod
    def copy(self, value: T, *, changes: dict[typing.Any, typing.Any]) -> T:
        """Copy the instance with the changes applied.

        Args:
            value: The instance to copy.
            changes: The changes to apply to the instance.

        Returns:
            The copied instance.
        """

    def wrap(self, value: T) -> WrappedValue[T]:
        """Wrap the value with the adapter.

        Args:
            value: The value to wrap.

        Returns:
            The wrapped value.
        """
        return WrappedValue(value, adapter=self)


class WrappedValue(typing.Generic[T]):
    """A wrapped value with an adapter."""

    value: T
    """The wrapped value."""

    adapter: BaseAdapter[T]
    """The adapter for the value."""

    def __init__(self, value: T, *, adapter: BaseAdapter[T]) -> None:
        self.value = value
        self.adapter = adapter

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WrappedValue):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def __str__(self) -> str:
        return str(self.value)

    def unwrap(self) -> T:
        return self.value

    def get_values(self) -> dict[typing.Any, typing.Any]:
        return self.adapter.get_values(self.value)

    def copy(self, *, changes: dict[typing.Any, typing.Any]) -> T:
        return self.adapter.copy(self.value, changes=changes)
