class AnyMergeError(Exception):
    """Base class for all AnyMerge exceptions."""


class AnyMergeTypeError(TypeError, AnyMergeError):
    """Raised when an invalid type is encountered."""


class AnyMergeValueError(ValueError, AnyMergeError):
    """Raised when an invalid value is encountered."""
