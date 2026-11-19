import dataclasses
import operator
import typing

import pytest

import anymerge.reducers as sut
from anymerge import Reducer, merge


@dataclasses.dataclass
class Todo:
    id: int
    done: bool = False


@pytest.mark.parametrize(
    ("key", "a", "b", "expected"),
    [
        pytest.param("id", [], [Todo(1)], [Todo(1)], id="append"),
        pytest.param(
            "id",
            [Todo(1), Todo(2)],
            [Todo(1, done=True)],
            [Todo(1, done=True), Todo(2)],
            id="replace-in-place",
        ),
        pytest.param("id", [Todo(1), Todo(2)], [sut.Remove(1)], [Todo(2)], id="remove"),
        pytest.param("id", [Todo(1)], [sut.Remove(9)], [Todo(1)], id="remove-missing"),
        pytest.param("id", [{"id": 1}], [{"id": 1, "x": 2}], [{"id": 1, "x": 2}], id="dict"),
        pytest.param(
            operator.itemgetter(0),
            [(1, "a")],
            [(1, "b"), (2, "c")],
            [(1, "b"), (2, "c")],
            id="callable",
        ),
    ],
)
def test_merge_by_key(key: typing.Any, a: typing.Any, b: typing.Any, expected: typing.Any):
    assert sut.merge_by_key(key)(a, b) == expected


def test_merge_by_key_in_merge():
    @dataclasses.dataclass
    class State:
        todos: typing.Annotated[list[Todo], Reducer(sut.merge_by_key("id"))]

    state = State(todos=[Todo(1), Todo(2)])
    result = merge(state, {"todos": [Todo(1, done=True), sut.Remove(2), Todo(3)]})
    assert result == State(todos=[Todo(1, done=True), Todo(3)])
