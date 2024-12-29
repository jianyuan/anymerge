import abc
import typing

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
