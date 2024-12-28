class AnyMergeError(Exception):
    pass


class AnyMergeTypeError(TypeError, AnyMergeError):
    pass


class AnyMergeValueError(ValueError, AnyMergeError):
    pass
