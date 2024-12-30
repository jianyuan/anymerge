import anymerge._reducer as sut
from tests.adapters import fixtures


def test_reduce():
    assert sut.reduce(
        fixtures.PydanticModel4(a=0),
        [
            fixtures.DataclassModel2(a=1),
            fixtures.PydanticModel2(a=2),
            fixtures.PydanticV1Model2(a=3),
        ],
    ) == fixtures.PydanticModel4(a=6)
