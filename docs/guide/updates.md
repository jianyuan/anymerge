# Updates

The second argument to `merge` is the update. anymerge merges each of its fields that the base also has, and ignores the rest unless the base is a Pydantic model that allows [extra fields](../models/pydantic.md#extra-fields). The examples on this page use Pydantic models, which need the [`pydantic` extra](../models/pydantic.md), and everything here works the same for [dataclasses](../models/dataclasses.md) and [TypedDicts](../models/typeddicts.md).

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

When the update is a model, which of its fields count depends on its type:

- A [Pydantic model](../models/pydantic.md#partial-updates) contributes only the fields that were set explicitly.
- A [dataclass](../models/dataclasses.md#updates-merge-every-field) contributes every field, defaults included.
- A [TypedDict](../models/typeddicts.md#updates) is a plain dict, so it contributes the keys it contains.

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

Pass `Overwrite` in a dict update. A Pydantic model [rejects it](../models/pydantic.md#markers-go-in-dict-updates) when it validates the field.

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
