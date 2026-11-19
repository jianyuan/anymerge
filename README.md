# anymerge

[![PyPI - Version](https://img.shields.io/pypi/v/anymerge.svg)](https://pypi.org/project/anymerge)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/anymerge.svg)](https://pypi.org/project/anymerge)

anymerge merges dataclasses, TypedDicts and Pydantic models field by field. A reducer in each field's type annotation decides how the old and new values combine, and `merge` returns a new instance.

```python
import dataclasses
import operator
from typing import Annotated

from anymerge import Reducer, merge

@dataclasses.dataclass
class State:
    status: str
    total: Annotated[int, Reducer(operator.add)] = 0
    log: Annotated[list[str], Reducer(operator.add)] = dataclasses.field(default_factory=list)


state = State(status="pending")
state = merge(state, {"status": "running", "total": 3, "log": ["started"]})
state = merge(state, {"total": 2, "log": ["finished"]})

print(state)
#> State(status='running', total=5, log=['started', 'finished'])
```

`status` has no reducer, so it takes the new value. `total` and `log` are combined with `operator.add`.

## Features

- Any two-argument function works as a reducer: `operator.add`, `operator.or_`, `max`, or your own.
- `Reducer(...)` merges a nested model field by field instead of replacing it.
- Partial updates: a dict changes only the keys it has, and a Pydantic model only the fields that were set explicitly.
- `Overwrite(value)` replaces a field without running its reducer.
- `merge_by_key("id")` updates, appends and, with `Remove(key)`, deletes items in a list of records.
- `reduce(state, updates)` applies a sequence of updates in order.
- Fully typed: `merge` and `reduce` return the type of the model you pass in.

## Installation

```console
pip install anymerge
```

To merge Pydantic models, install the `pydantic` extra, which adds Pydantic 2:

```console
pip install "anymerge[pydantic]"
```

anymerge needs Python 3.11 or later.

## Why anymerge?

Dict-merging libraries such as mergedeep and deepmerge pick a strategy per call or per Python type, and they modify their first argument in place. anymerge sets the rule on each field of a typed model and leaves its arguments unchanged.

Pydantic's `model_copy(update=...)` replaces each field you pass with the new value. It can't add to the old value, and it replaces a nested model as a whole.

## Documentation

The [documentation](https://anymerge.jian.fyi) covers supported models, reducers, updates and lists of records, and has an API reference. Changes are listed in the [release notes](https://github.com/jianyuan/anymerge/releases), and bugs and ideas go in the [issue tracker](https://github.com/jianyuan/anymerge/issues).

anymerge is at version 0.x, so a minor release can still change the API. Patch releases never do, and breaking changes are called out in the release notes. See the [stability policy](https://anymerge.jian.fyi/stability/).

## License

anymerge is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
