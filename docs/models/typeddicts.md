# TypedDicts

TypedDicts need nothing beyond `pip install anymerge`. Annotate a key with a `Reducer` to set how it merges.

A TypedDict instance is a plain dict at runtime, so anymerge can't tell which TypedDict it belongs to. Wrap the base with `TypedDictAdapter` to give it the type:

```python
import operator
from typing import Annotated, TypedDict

from anymerge import Reducer, merge
from anymerge.adapters import TypedDictAdapter

class State(TypedDict):
    name: str
    tags: Annotated[list[str], Reducer(operator.add)]


state = TypedDictAdapter(State).wrap(State(name="a", tags=["x"]))

print(merge(state, {"tags": ["y"]}))
#> {'name': 'a', 'tags': ['x', 'y']}
```

The result is a new plain dict, not a wrapped one. Type checkers see `merge` and `reduce` return `State`. Wrap the result again before using it as the base of another merge. `reduce` does that for you between updates:

```python
import operator
from typing import Annotated, TypedDict

from anymerge import Reducer, reduce
from anymerge.adapters import TypedDictAdapter

class State(TypedDict):
    total: Annotated[int, Reducer(operator.add)]


state = TypedDictAdapter(State).wrap(State(total=0))

print(reduce(state, [{"total": 1}, {"total": 2}]))
#> {'total': 3}
```

## Updates

An update is a dict, or another TypedDict instance, which is also a plain dict. Only the keys it contains are merged.

## Keys that aren't required

When a `NotRequired` key, or a key of a `total=False` TypedDict, is missing from the base, there's no current value to reduce with. `merge` uses the update's value as it is:

```python
import operator
from typing import Annotated, NotRequired, TypedDict

from anymerge import Reducer, merge
from anymerge.adapters import TypedDictAdapter

class State(TypedDict):
    tags: NotRequired[Annotated[list[str], Reducer(operator.add)]]


print(merge(TypedDictAdapter(State).wrap(State()), {"tags": ["x"]}))
#> {'tags': ['x']}
```

## Limitations

- `Reducer(...)` can't deep-merge a TypedDict nested inside another TypedDict, because the nested value is a plain dict with no type attached. Use a dataclass or Pydantic model for nested state that needs deep merging.
- `merge` doesn't check types, so a reducer or update can put a value of the wrong type in a key.
