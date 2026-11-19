# Choosing a model

anymerge works with three kinds of model: dataclasses, Pydantic models and TypedDicts. They are declared the same way, with a `Reducer` inside `Annotated` on each field, but they differ in what you install, what counts as an update and what `merge` gives back.

| | [Dataclasses](dataclasses.md) | [Pydantic models](pydantic.md) | [TypedDicts](typeddicts.md) |
| --- | --- | --- | --- |
| Install | `pip install anymerge` | `pip install "anymerge[pydantic]"` | `pip install anymerge` |
| As the base | The instance | The instance | Wrapped with `TypedDictAdapter` |
| As an update, merges | Every field | Fields set explicitly | The keys present |
| `merge` returns | A new instance, via `dataclasses.replace` | A new instance, via `model_copy` | A plain dict |
| Update keys the base doesn't declare | Ignored | Ignored, or kept with `extra="allow"` | Ignored |
| Validation after merge | None | None | None |

The first argument to `merge` is the base, the instance being updated. Its type annotations hold the reducers. The second argument is the update.

## Plain dicts

A plain dict has no annotations, so it can't be the base, and passing one raises `AnyMergeTypeError`. As an update, a dict works with every kind of base and changes only the keys it contains. It's the simplest way to send a partial update.

## Mixing types

The update doesn't have to be the same type as the base. anymerge reads the update's fields by name and merges each one the base also has:

```python
import dataclasses
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

@dataclasses.dataclass
class State:
    total: Annotated[int, Reducer(operator.add)] = 0


class Event(BaseModel):
    total: int


print(merge(State(total=1), Event(total=2)))
#> State(total=3)
```

Each kind of update follows its own rule for which fields count: a Pydantic update only contributes the fields that were set, whatever the base is.
