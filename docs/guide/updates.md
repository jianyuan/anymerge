# Updates

The second argument to `merge` is the update. It can be a dict or any [supported model](models.md), and anymerge merges each of its fields that the base also has. Keys the base doesn't have are ignored.

## Partial updates

Only the fields in the update are merged, so a dict with a few keys changes only those fields:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    name: str = "default"
    total: Annotated[int, Reducer(operator.add)] = 0


state = State(name="kept", total=5)

print(merge(state, {"total": 1}))
#> name='kept' total=6
```

A Pydantic model as the update works the same way. Only the fields set explicitly when it was created are merged, so unset defaults don't overwrite existing values:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    name: str = "default"
    total: Annotated[int, Reducer(operator.add)] = 0


state = State(name="kept", total=5)

print(merge(state, State(total=1)))
#> name='kept' total=6
```

To reset a field to its default, set it explicitly, as in `State(name="default")`.

Dataclasses don't record which fields were set, so a dataclass update merges every field, defaults included. Use a dict to update only some fields of a dataclass.

## Overwriting a field

To replace a field's value without running its reducer, wrap the new value in `Overwrite`:

```python
import operator
from typing import Annotated

from anymerge import Overwrite, Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    items: Annotated[list[int], Reducer(operator.add)] = []


state = State(items=[1, 2])

print(merge(state, {"items": [3]}))
#> items=[1, 2, 3]
print(merge(state, {"items": Overwrite([])}))
#> items=[]
```

Pass `Overwrite` in a dict update. Pydantic models reject it when they validate the field.

`Overwrite` also works inside a [deep merge](reducers.md#deep-merging), at any level:

```python
import operator
from typing import Annotated

from anymerge import Overwrite, Reducer, merge
from pydantic import BaseModel

class Stats(BaseModel):
    count: Annotated[int, Reducer(operator.add)] = 0


class State(BaseModel):
    stats: Annotated[Stats, Reducer(...)] = Stats()


print(merge(State(stats=Stats(count=5)), {"stats": {"count": Overwrite(0)}}))
#> stats=Stats(count=0)
```

## Applying many updates

`reduce` merges a sequence of updates into a base, one after another:

```python
import operator
from typing import Annotated

from anymerge import Reducer, reduce
from pydantic import BaseModel

class State(BaseModel):
    status: str = "pending"
    log: Annotated[list[str], Reducer(operator.add)] = []


updates = [
    {"status": "running", "log": ["started"]},
    {"log": ["step 1 done"]},
    {"status": "done", "log": ["finished"]},
]

print(reduce(State(), updates))
#> status='done' log=['started', 'step 1 done', 'finished']
```

`reduce` takes the same `default_reducer` argument as `merge`.
