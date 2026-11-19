# Lists of records

`merge_by_key` is a reducer for lists of records that each have a key, such as an ID. It matches items in the update to items in the current list by key:

- An item with a matching key replaces the current one, in the same position.
- An item with a new key is appended.
- `Remove(key)` deletes the item with that key.

```python
from typing import Annotated

from anymerge import Reducer, Remove, merge
from anymerge.reducers import merge_by_key
from pydantic import BaseModel

class Todo(BaseModel):
    id: int
    done: bool = False


class State(BaseModel):
    todos: Annotated[list[Todo], Reducer(merge_by_key("id"))] = []


state = State(todos=[Todo(id=1), Todo(id=2)])

print(merge(state, {"todos": [Todo(id=1, done=True), Remove(2), Todo(id=3)]}))
#> todos=[Todo(id=1, done=True), Todo(id=3, done=False)]
```

Like `Overwrite`, `Remove` goes in a dict update, because Pydantic models reject it when they validate the field.

## Choosing the key

The key can be a field name or a function. A field name works for items that are dicts, dataclasses or Pydantic models. A function takes an item and returns its key:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from anymerge.reducers import merge_by_key
from pydantic import BaseModel

class State(BaseModel):
    scores: Annotated[list[tuple[str, int]], Reducer(merge_by_key(operator.itemgetter(0)))] = []


state = State(scores=[("alice", 1), ("bob", 2)])

print(merge(state, {"scores": [("bob", 5), ("carol", 3)]}))
#> scores=[('alice', 1), ('bob', 5), ('carol', 3)]
```

## Edge cases

- Removing a key that isn't in the list does nothing, so applying the same update twice gives the same result.
- If the current list has several items with the same key, they are all kept. An update or `Remove` for that key applies to every one of them.
- If the update repeats a key, the last item with that key wins.
- An item that has no field named after the key raises `AnyMergeValueError`.
- A matched item replaces the current one entirely. Its fields aren't merged.
