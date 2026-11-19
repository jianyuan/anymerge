# Pydantic models

Pydantic 2 models need the `pydantic` extra:

```console
$ pip install "anymerge[pydantic]"
```

The extra installs Pydantic. anymerge itself never imports it. Annotate a field with a `Reducer` to set how it merges:

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

`merge` builds the result with `model_copy`, so the base is left unchanged and frozen models work. `model_copy` doesn't run validation, so a reducer or update can put a value of the wrong type in a field. Call `model_validate` on the result if you need it checked.

## Partial updates

When a Pydantic model is the update, only the fields set explicitly when it was created are merged. Unset defaults don't overwrite existing values:

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

To reset a field to its default, set it explicitly, as in `State(name="default")`. A field that has a reducer still runs it, so use [`Overwrite`](../guide/updates.md#overwriting-a-field) to replace its value instead.

## Aliases

A dict update can use a field's name, its `alias` or a string `validation_alias`, so a request body that arrives under its aliases merges as expected:

```python
from anymerge import merge
from pydantic import BaseModel, Field

class User(BaseModel):
    full_name: str = Field(alias="fullName")
    email: str = ""


user = User(fullName="Ada")

print(merge(user, {"fullName": "Ada Lovelace"}))
#> full_name='Ada Lovelace' email=''
```

Using both the name and an alias for the same field in one update raises `AnyMergeValueError`. `AliasChoices` and `AliasPath` aren't supported.

## Extra fields

Keys the model doesn't declare are ignored, unless the model is configured with `extra="allow"`. Then they are merged with the default reducer, which replaces them unless you pass a different `default_reducer`:

```python
from anymerge import merge
from pydantic import BaseModel, ConfigDict

class Event(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str


print(merge(Event(name="signup", source="web"), {"source": "app", "campaign": "spring"}))
#> name='signup' source='app' campaign='spring'
```

## Markers go in dict updates

`Overwrite` and `Remove` wrap values that don't match the field's type, so `State(items=Overwrite([]))` raises a `ValidationError`. Pass them in a dict update instead:

```python
import operator
from typing import Annotated

from anymerge import Overwrite, Reducer, merge
from pydantic import BaseModel

class State(BaseModel):
    items: Annotated[list[int], Reducer(operator.add)] = []


print(merge(State(items=[1, 2]), {"items": Overwrite([])}))
#> items=[]
```
