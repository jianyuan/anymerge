# anymerge

Anymerge is a library for merging dataclasses, TypedDicts, and Pydantic models seamlessly with custom reducers.

## Examples

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    replace: str # (1)!
    total: Annotated[int, Reducer(operator.add)] # (2)!


original_state = State(
    replace="original",
    total=0,
)
new_state = State(
    replace="replace",
    total=1,
)

final = merge(original_state, new_state)
print(final)
#> replace='replace' total=1
```

1. By default, the field value is replaced with the value from the new state.
2. By annotating the field with a `Reducer`, you can specify a custom reducer function for the field. In this example, the `total` field uses the `operator.add` function as its reducer. This means that when merging, the values of the `total` field from both states will be added together instead of the default behavior of replacing the value.

### Partial updates

Only the fields in the update are merged. For a Pydantic model, that means the fields set explicitly when it was created, so unset defaults never overwrite existing values. A plain dict works too:

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
print(merge(state, {"total": 1}))
#> name='kept' total=6
```

To reset a field to its default, set it explicitly: `State(name="default")`.

### Overwriting a field

To replace a field's value without running its reducer, wrap the new value in `Overwrite`. Pass it in a dict update, because Pydantic models reject an `Overwrite` value when they validate:

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

## Installation

```console
$ pip install anymerge
```

## License

`anymerge` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
