# Agent state

An agent loop keeps state between steps: the conversation so far, how many tokens it has used, notes, and the results of its tools. Each step returns an update, and the loop merges it in. The reducers on the state model decide what happens to each field, so the steps don't need to know about each other.

## Message history

Append new messages with `operator.add`. To edit or delete a message after the fact, such as when a user edits their prompt or you trim an old tool result, give each message an ID and use [`merge_by_key`](../guide/lists.md) instead:

```python
from typing import Annotated, Literal

from anymerge import Reducer, Remove, merge
from anymerge.reducers import merge_by_key
from pydantic import BaseModel

class Message(BaseModel):
    id: str
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class State(BaseModel):
    messages: Annotated[list[Message], Reducer(merge_by_key("id"))] = []


state = State()
state = merge(state, {"messages": [Message(id="1", role="user", content="Hi")]})
state = merge(state, {"messages": [Message(id="2", role="assistant", content="Hello!")]})

# The user edits their message, and the stale reply is removed.
state = merge(state, {"messages": [Message(id="1", role="user", content="Hi there"), Remove("2")]})

for message in state.messages:
    print(message.role, message.content)
#> user Hi there
```

New IDs are appended, so `merge_by_key` also does the plain append. Pydantic checks every message's `role`, so a step can't add a message with a role your prompt builder doesn't know.

## Token usage

Most SDKs report usage per call, and a run makes many calls. Put the counts in a nested model and merge it field by field with `Reducer()`, adding each count:

```python
import operator
from typing import Annotated

from anymerge import Reducer, reduce
from pydantic import BaseModel

class Usage(BaseModel):
    requests: Annotated[int, Reducer(operator.add)] = 0
    input_tokens: Annotated[int, Reducer(operator.add)] = 0
    output_tokens: Annotated[int, Reducer(operator.add)] = 0


class State(BaseModel):
    answer: str = ""
    usage: Annotated[Usage, Reducer()] = Usage()


calls = [
    {"usage": Usage(requests=1, input_tokens=1200, output_tokens=80)},
    {"usage": Usage(requests=1, input_tokens=1350, output_tokens=40)},
    {"answer": "42", "usage": Usage(requests=1, input_tokens=1400, output_tokens=12)},
]

print(reduce(State(), calls))
#> answer='42' usage=Usage(requests=3, input_tokens=3950, output_tokens=132)
```

Usage from a sub-agent merges the same way. The sub-agent returns its `Usage`, and the parent merges it into its own state, so the two never share a mutable counter.

## Parallel branches

When an orchestrator runs several sub-agents or tool calls at once, have each one return an update instead of writing to shared state. Once they've all finished, merge the updates in one step:

```python
import asyncio
import operator
from typing import Annotated

from anymerge import Reducer, reduce
from pydantic import BaseModel

class Research(BaseModel):
    question: str
    sources: Annotated[set[str], Reducer(operator.or_)] = set()
    notes: Annotated[list[str], Reducer(operator.add)] = []


async def search_web(question: str) -> Research:
    return Research(question=question, sources={"web"}, notes=["Found 3 articles"])


async def search_papers(question: str) -> Research:
    return Research(question=question, sources={"arxiv"}, notes=["Found 1 paper"])


async def main() -> Research:
    state = Research(question="What is RLHF?")
    updates = await asyncio.gather(search_web(state.question), search_papers(state.question))
    return reduce(state, updates)


state = asyncio.run(main())
print(sorted(state.sources), state.notes)
#> ['arxiv', 'web'] ['Found 3 articles', 'Found 1 paper']
```

`asyncio.gather` returns results in the order you passed the calls, so `notes` is in a fixed order even though the branches can finish in any order. No branch sees another's partial writes, and there's no lock to hold.

A field without a reducer takes the value from whichever update comes last. If two branches both set it, the earlier value is lost without an error. Give every field that more than one branch writes a reducer, or have only one branch write it.

## Updates proposed by a model

Some agents let the model change its own state, for example by calling an `update_plan` tool. Validate the tool's arguments as a Pydantic model and merge the result. Fields the model left out aren't set, so they don't reset anything:

```python
import operator
from typing import Annotated, Literal

from anymerge import Reducer, merge
from pydantic import BaseModel

class Plan(BaseModel):
    goal: str = ""
    status: Literal["planning", "working", "done"] = "planning"
    steps: Annotated[list[str], Reducer(operator.add)] = []


state = Plan(goal="Book a flight", steps=["Search flights"])

tool_arguments = '{"status": "working", "steps": ["Compare prices"]}'
state = merge(state, Plan.model_validate_json(tool_arguments))

print(state)
#> goal='Book a flight' status='working' steps=['Search flights', 'Compare prices']
```

An argument that doesn't validate, such as `"status": "finished"`, raises `ValidationError` before anything is merged, and you can send the error back to the model as the tool result.

## Human review

When a person reviews the agent's state, their edit should replace a value outright, not go through the reducer. Wrap it in [`Overwrite`](../guide/updates.md#overwriting-a-field):

```python
import operator
from typing import Annotated

from anymerge import Overwrite, Reducer, merge
from pydantic import BaseModel

class Plan(BaseModel):
    steps: Annotated[list[str], Reducer(operator.add)] = []


state = Plan(steps=["Search flights", "Compare prices", "Search hotels"])
state = merge(state, {"steps": Overwrite(["Search flights", "Book the cheapest"])})

print(state.steps)
#> ['Search flights', 'Book the cheapest']
```

## Replaying a log of updates

If you store each step's update instead of the whole state, `reduce` rebuilds the state at any point by folding the log from the start. That gives you checkpoints, time travel and debugging from the same data:

```python
import operator
from typing import Annotated

from anymerge import Reducer, reduce
from pydantic import BaseModel

class State(BaseModel):
    step: Annotated[int, Reducer(operator.add)] = 0
    notes: Annotated[list[str], Reducer(operator.add)] = []


log = [
    {"step": 1, "notes": ["searched"]},
    {"step": 1, "notes": ["read page"]},
    {"step": 1, "notes": ["answered"]},
]

print(reduce(State(), log[:2]))
#> step=2 notes=['searched', 'read page']
```

Store the updates as JSON and validate each one as you read it back, for example with a `TypeAdapter` for the update's shape, so a corrupt log entry fails loudly.
