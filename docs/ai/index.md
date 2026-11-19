# AI applications

Most AI code needs to combine many partial results into one object. An agent's tools and sub-agents each return part of the state. A streamed response arrives as dozens of small deltas. Several retrievers each return their own list of documents. An extraction job runs the same prompt on every chunk of a long document. Each case needs a rule for every field: append the messages, add up the token counts, keep the highest score, replace the status.

anymerge lets you write those rules once, on the model, and then fold any number of updates into it with `merge` or `reduce`. The pages in this section show the common cases:

| Page | What it merges |
| --- | --- |
| [Agent state](agent-state.md) | Message history, token usage, results from parallel branches, patches proposed by a model |
| [Streaming responses](streaming.md) | Text and tool-call deltas from a streamed chat completion |
| [Retrieval](retrieval.md) | Documents from several retrievers or queries, deduplicated by ID |
| [Structured extraction](extraction.md) | Partial records extracted from each chunk of a long document |
| [Model settings](settings.md) | Default, provider and per-request generation settings |
| [Evaluation results](evals.md) | Metrics and case results from shards of an eval run |

The examples use plain Pydantic models in place of any SDK's types, so they run with only `anymerge[pydantic]` installed. Each one works the same way with the objects an SDK returns once you convert them to dicts or to your own models.

## Validate before you merge

Output from a model is untrusted input. Parse it into a Pydantic model before it reaches `merge`, so a malformed or out-of-range value is rejected at the boundary instead of ending up in your state:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel, Field, ValidationError

class Findings(BaseModel):
    facts: Annotated[list[str], Reducer(operator.add)] = []
    confidence: Annotated[float, Reducer(max), Field(ge=0, le=1)] = 0


state = Findings()
state = merge(state, Findings.model_validate_json('{"facts": ["The sky is blue"], "confidence": 0.9}'))

try:
    merge(state, Findings.model_validate_json('{"confidence": 7}'))
except ValidationError as e:
    print(e.errors()[0]["msg"])
#> Input should be less than or equal to 1

print(state)
#> facts=['The sky is blue'] confidence=0.9
```

A validated Pydantic model also makes a safe partial update. Only the fields the model's output actually contained were set, so `merge` applies those and leaves the rest of the state alone. Its defaults never overwrite values you've already collected. See [Partial updates](../models/pydantic.md#partial-updates).

`merge` builds its result with `model_copy`, which doesn't run validation. A reducer can return a value that breaks a constraint, such as a sum that goes past a limit. If that matters, check the result with `model_validate`:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge
from pydantic import BaseModel, Field, ValidationError

class Budget(BaseModel):
    tokens: Annotated[int, Reducer(operator.add), Field(le=1000)] = 0


state = merge(Budget(tokens=900), Budget(tokens=200))

try:
    Budget.model_validate(state.model_dump())
except ValidationError as e:
    print(e.errors()[0]["msg"])
#> Input should be less than or equal to 1000
```

## Order of updates

Updates from parallel work can finish in any order. If every field's reducer gives the same result in any order, such as `operator.add` on numbers, `operator.or_` on sets, `max` and `min`, the merged state is the same however the updates arrive. Reducers that keep the last value, appending to a list, and [`merge_by_key`](../guide/lists.md) all depend on order. When that matters, collect the updates and apply them in a fixed order with `reduce`, for example sorted by branch or chunk number.
