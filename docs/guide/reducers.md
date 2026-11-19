# Reducers

A reducer is a function that takes a field's current value and its new value, and returns the merged value. You attach one to a field with `Reducer` inside `Annotated`:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    name: str
    total: Annotated[int, Reducer(operator.add)]


print(merge(State(name="a", total=1), State(name="b", total=2)))
#> name='b' total=3
```

A field without a reducer takes the new value. Fields the update doesn't contain are left as they are. The examples on this page use Pydantic models, and reducers work the same way on [dataclasses](../models/dataclasses.md) and [TypedDicts](../models/typeddicts.md).

## Common reducers

Any function that takes the current value and the new value works as a reducer, so the standard library covers most cases:

| Reducer | Use it for | Result |
| --- | --- | --- |
| `operator.add` | Appending to lists, summing numbers, joining strings | `[1] + [2]` → `[1, 2]` |
| `operator.or_` | Set union, shallow dict update | `or_({"x": 1, "y": 1}, {"y": 2})` → `{"x": 1, "y": 2}` |
| `max`, `min` | Keeping the highest or lowest value | `max(3, 5)` → `5` |
| [`merge_by_key`](lists.md) | Updating a list of records by key | See [Lists of records](lists.md) |

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    tags: Annotated[set[str], Reducer(operator.or_)] = set()
    meta: Annotated[dict[str, int], Reducer(operator.or_)] = {}
    high_score: Annotated[int, Reducer(max)] = 0


state = State(tags={"a"}, meta={"x": 1, "y": 1}, high_score=5)

result = merge(state, {"tags": {"b"}, "meta": {"y": 2}, "high_score": 3})
print(sorted(result.tags), result.meta, result.high_score)
#> ['a', 'b'] {'x': 1, 'y': 2} 5
```

## Custom reducers

Write your own function when the standard library doesn't fit. This one keeps the first value a field ever gets:

```python
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

def keep_first(current, new):
    return new if current is None else current


class State(BaseModel):
    started_by: Annotated[str | None, Reducer(keep_first)] = None


state = merge(State(), {"started_by": "alice"})
state = merge(state, {"started_by": "bob"})

print(state)
#> started_by='alice'
```

## Several reducers on one field

When a field has more than one `Reducer`, they run in order. Each one gets the result of the one before it as the current value, and the same new value:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

def at_most_10(current, _new):
    return min(current, 10)


class State(BaseModel):
    total: Annotated[int, Reducer(operator.add), Reducer(at_most_10)] = 0


print(merge(State(total=8), {"total": 5}))
#> total=10
```

## Changing the default

`merge` and `reduce` take a `default_reducer`, which applies to every field that has no reducer of its own:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class Counts(BaseModel):
    apples: int = 0
    pears: int = 0
    best: Annotated[int, Reducer(max)] = 0


counts = Counts(apples=1, pears=2, best=5)
update = {"apples": 3, "pears": 1, "best": 4}

print(merge(counts, update, default_reducer=Reducer(operator.add)))
#> apples=4 pears=3 best=5
```

## Deep merging

By default, a field holding a nested model is replaced as a whole. `Reducer(...)`, or its long form `Reducer(deep=True)`, merges the nested model field by field instead, using the nested model's own reducers:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class Stats(BaseModel):
    count: Annotated[int, Reducer(operator.add)] = 0
    label: str = ""


class State(BaseModel):
    deep: Annotated[Stats, Reducer(...)] = Stats()
    shallow: Stats = Stats()


state = State(deep=Stats(count=1, label="a"), shallow=Stats(count=1, label="a"))

print(merge(state, {"deep": {"count": 2}, "shallow": Stats(count=2)}))
#> deep=Stats(count=3, label='a') shallow=Stats(count=2, label='')
```

`deep` kept its label and added the counts. `shallow` was replaced by the new `Stats`, so its label went back to the default.
