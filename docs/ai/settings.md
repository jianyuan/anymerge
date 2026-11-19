# Model settings

Generation settings usually come in layers: your app's defaults, then settings for a provider or model, then overrides for a single request. A plain dict update (`defaults | overrides`) handles flat values like `temperature`, but replaces nested values as a whole. A request that adds one HTTP header would drop every header the earlier layers set.

Put a reducer on the fields that need more than replacing:

```python
import operator
from typing import Annotated

from anymerge import Reducer, reduce
from pydantic import BaseModel, Field

class ModelSettings(BaseModel):
    model: str = "small"
    temperature: Annotated[float, Field(ge=0, le=2)] = 1.0
    max_tokens: Annotated[int, Reducer(min), Field(gt=0)] = 4096
    stop: Annotated[list[str], Reducer(operator.add)] = []
    headers: Annotated[dict[str, str], Reducer(operator.or_)] = {}


defaults = ModelSettings(headers={"x-app": "docs-bot"})
provider = ModelSettings(model="large", max_tokens=2048, headers={"x-team": "search"})
request = ModelSettings(temperature=0.2, stop=["\n\n"], headers={"x-request-id": "r1"})

print(reduce(defaults, [provider, request]).model_dump())
#> {'model': 'large', 'temperature': 0.2, 'max_tokens': 2048, 'stop': ['\n\n'], 'headers': {'x-app': 'docs-bot', 'x-team': 'search', 'x-request-id': 'r1'}}
```

- `model` and `temperature` have no reducer, so the most specific layer that sets them wins.
- `max_tokens` uses `min`, so a request can lower the limit but never raise it above what the provider layer allows.
- `stop` collects stop sequences from every layer.
- `headers` merges key by key with `operator.or_`, so each layer adds its own headers.

Every layer is a validated `ModelSettings`, so a request with `temperature=5` fails when it's built, not when the provider rejects the call. Each layer also contributes only the fields it set, so `request` doesn't reset `model` back to `"small"`.

## Clearing a value

To remove headers or stop sequences an earlier layer set, use [`Overwrite`](../guide/updates.md#overwriting-a-field) in a dict update:

```python
import operator
from typing import Annotated

from anymerge import Overwrite, Reducer, merge
from pydantic import BaseModel

class ModelSettings(BaseModel):
    headers: Annotated[dict[str, str], Reducer(operator.or_)] = {}


settings = ModelSettings(headers={"x-app": "docs-bot", "x-debug": "1"})

print(merge(settings, {"headers": Overwrite({"x-app": "docs-bot"})}))
#> headers={'x-app': 'docs-bot'}
```

## Where this fits

Libraries such as pydantic-settings load configuration once at startup, from files, environment variables and the command line. anymerge is for the layering that happens at run time, per tenant, per agent or per request, after that configuration has been loaded.
