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

final = merge(original, new_state)
print(final)
#> State(replace='replace', total=1)
```

1. By default, the field value is replaced with the value from the new state.
2. By annotating the field with a `Reducer`, you can specify a custom reducer function for the field. In this example, the `total` field uses the `operator.add` function as its reducer. This means that when merging, the values of the `total` field from both states will be added together instead of the default behavior of replacing the value.

## Installation

```console
$ pip install anymerge
```

## License

`anymerge` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
