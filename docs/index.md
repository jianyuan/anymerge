# anymerge

anymerge merges dataclasses, TypedDicts and Pydantic models field by field. Each field decides how its old and new values combine, using a reducer declared in the field's type annotation.

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    status: str  # (1)!
    total: Annotated[int, Reducer(operator.add)]  # (2)!
    log: Annotated[list[str], Reducer(operator.add)] = []


state = State(status="pending", total=0)
state = merge(state, {"status": "running", "total": 3, "log": ["started"]})
state = merge(state, {"total": 2, "log": ["finished"]})

print(state)
#> status='running' total=5 log=['started', 'finished']
```

1. A field without a reducer takes the new value.
2. `Reducer(operator.add)` adds the new value to the old one.

`merge` returns a new instance and doesn't modify either argument, as long as your reducers don't modify their inputs.

## Installation

```console
$ pip install anymerge
```

To merge Pydantic models, install the `pydantic` extra, which adds Pydantic 2:

```console
$ pip install "anymerge[pydantic]"
```

anymerge needs Python 3.11 or later. Dataclasses and TypedDicts work without any other dependency.

## Where to go next

- [Choosing a model](models/index.md) compares dataclasses, Pydantic models and TypedDicts, and each has its own page: [dataclasses](models/dataclasses.md), [Pydantic models](models/pydantic.md) and [TypedDicts](models/typeddicts.md).
- [Reducers](guide/reducers.md) explains how fields combine, including custom reducers and deep merging.
- [Updates](guide/updates.md) covers partial updates, `Overwrite` and applying many updates with `reduce`.
- [Lists of records](guide/lists.md) shows how to update, append and remove items by key.
- The API reference documents every public function and class.

## License

anymerge is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
