# Dataclasses

Dataclasses need nothing beyond `pip install anymerge`. Annotate a field with a `Reducer` to set how it merges:

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

`merge` builds the result with `dataclasses.replace`, so the base is left unchanged and frozen dataclasses work. Dataclasses declared with `slots=True` work too.

## Updates merge every field

A dataclass doesn't record which fields were set when it was created. When a dataclass is the update, every field is merged, defaults included:

```python
import dataclasses

from anymerge import merge

@dataclasses.dataclass
class State:
    name: str = "default"
    count: int = 0


state = State(name="kept", count=1)

print(merge(state, State(count=2)))
#> State(name='default', count=2)
print(merge(state, {"count": 2}))
#> State(name='kept', count=2)
```

Use a dict when you want to change only some fields.

## String annotations

Reducers work in modules that use `from __future__ import annotations`, where annotations are stored as strings. anymerge resolves them with `typing.get_type_hints`. If an annotation can't be resolved, for example because it names a class defined inside a function, `merge` raises `AnyMergeTypeError` naming the dataclass.

## Limitations

- A field declared with `field(init=False)` can't be updated. `dataclasses.replace` rejects it and `merge` raises `TypeError`. Merges that leave the field out work as usual.
- `dataclasses.replace` runs `__post_init__` again. An `InitVar` is passed its default value, not the value the base was created with.
- `merge` doesn't check types, so a reducer or update can put a value of the wrong type in a field.
