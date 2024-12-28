import operator

import pytest

import anymerge.models as sut
from anymerge.exceptions import AnyMergeValueError


def test_reducer_info_validation():
    with pytest.raises(AnyMergeValueError) as excinfo:
        sut.ReducerInfo(operator.add, deep=True)

    assert str(excinfo.value) == "deep cannot be True when reducer is provided"
