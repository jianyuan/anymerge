# Supported models

The first argument to `merge` is the base: the instance being updated. It must be a model type that anymerge can read field annotations from. The second argument is the update, which can be any supported model or a plain dict.

| Type | As the base | As the update |
| --- | --- | --- |
| Dataclass | Yes | Yes |
| Pydantic model | Yes | Yes |
| TypedDict | Yes, wrapped with `TypedDictAdapter` | Yes |
| Plain dict | No | Yes |

## Dataclasses

Annotate fields with `Annotated` the same way as on any other model:

```python
import dataclasses
import operator
from typing import Annotated

from anymerge import Reducer, merge

@dataclasses.dataclass
class State:
    name: str
    tags: Annotated[list[str], Reducer(operator.add)] = dataclasses.field(default_factory=list)


print(merge(State(name="a", tags=["x"]), {"tags": ["y"]}))
#> State(name='a', tags=['x', 'y'])
```

The result is built with `dataclasses.replace`, so frozen dataclasses work too.

## Pydantic models

Pydantic 2 models are supported once you install the `pydantic` extra (`pip install "anymerge[pydantic]"`). The result is built with `model_copy`, which does not run validation again:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    name: str
    tags: Annotated[list[str], Reducer(operator.add)] = []


print(merge(State(name="a", tags=["x"]), {"tags": ["y"]}))
#> name='a' tags=['x', 'y']
```

When a Pydantic model is the update, only the fields that were set explicitly are merged. See [Partial updates](updates.md#partial-updates).

## TypedDicts

A TypedDict instance is a plain dict at runtime, so anymerge cannot tell which TypedDict it belongs to. Wrap the base with `TypedDictAdapter` to give it the type. The result is a plain dict:

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

## Plain dicts

A plain dict has no annotations, so it can't be the base. Passing one raises `AnyMergeTypeError`. As an update, a dict is the simplest way to change only some fields.

## Mixing types

The update doesn't have to be the same type as the base. anymerge reads its field values by name and merges every field the base also has:

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
