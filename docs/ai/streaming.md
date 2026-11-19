# Streaming responses

A streamed chat completion arrives as many small chunks. Each chunk holds a delta: a few characters of text, part of a tool call's arguments, or the finish reason. To get the whole message you fold the deltas together, and each field needs its own rule:

| Field | Rule |
| --- | --- |
| Text content | Concatenate |
| Tool calls | Match by `index` and merge each call's fragments |
| Tool call arguments | Concatenate the JSON fragments, and parse them once the stream ends |
| Finish reason | Keep the last value that isn't `null` |

The examples here use the shape of OpenAI's Chat Completions deltas. Other providers and gateways that copy that format send the same shape.

## Text

Text fields start empty and each delta adds a piece. Deltas can send `null` for content they don't carry, so the reducer treats `None` as an empty string:

```python
from typing import Annotated

from anymerge import Reducer, reduce
from pydantic import BaseModel

def concat(current: str | None, new: str | None) -> str:
    return (current or "") + (new or "")


def last_non_null(current, new):
    return current if new is None else new


class Message(BaseModel):
    role: str | None = None
    content: Annotated[str | None, Reducer(concat)] = None
    finish_reason: Annotated[str | None, Reducer(last_non_null)] = None


chunks = [
    '{"role": "assistant", "content": ""}',
    '{"content": "Hello"}',
    '{"content": ", world"}',
    '{"content": null, "finish_reason": "stop"}',
]

print(reduce(Message(), (Message.model_validate_json(chunk) for chunk in chunks)))
#> role='assistant' content='Hello, world' finish_reason='stop'
```

Each chunk is validated as a `Message`, which sets only the fields the chunk contains, so the `role` from the first chunk survives every later one.

## Tool calls

The model can call several tools in one message, and the stream interleaves their fragments. The first fragment of each call carries its `id` and function `name`. Later fragments carry only the call's `index` and the next piece of its arguments, so match calls by `index`, not `id`.

[`merge_by_key`](../guide/lists.md) replaces a matched item, which would throw away the earlier fragments. Instead, write a reducer that merges a matched item into the current one with `merge`, so the item model's own reducers concatenate the arguments:

```python
from typing import Annotated

from anymerge import Reducer, merge, reduce
from pydantic import BaseModel

def concat(current: str | None, new: str | None) -> str:
    return (current or "") + (new or "")


def merge_by_index(current: list, new: list) -> list:
    calls = {call.index: call for call in current}
    for call in new:
        calls[call.index] = merge(calls[call.index], call) if call.index in calls else call
    return sorted(calls.values(), key=lambda call: call.index)


class Function(BaseModel):
    name: str | None = None
    arguments: Annotated[str, Reducer(concat)] = ""


class ToolCall(BaseModel):
    index: int
    id: str | None = None
    function: Annotated[Function, Reducer()] = Function()


class Message(BaseModel):
    tool_calls: Annotated[list[ToolCall], Reducer(merge_by_index)] = []


chunks = [
    '{"tool_calls": [{"index": 0, "id": "call_a", "function": {"name": "get_weather", "arguments": ""}}]}',
    '{"tool_calls": [{"index": 0, "function": {"arguments": "{\\"city\\": "}}]}',
    '{"tool_calls": [{"index": 1, "id": "call_b", "function": {"name": "get_time", "arguments": "{}"}}]}',
    '{"tool_calls": [{"index": 0, "function": {"arguments": "\\"Paris\\"}"}}]}',
]

message = reduce(Message(), (Message.model_validate_json(chunk) for chunk in chunks))

for call in message.tool_calls:
    print(call.id, call.function.name, call.function.arguments)
#> call_a get_weather {"city": "Paris"}
#> call_b get_time {}
```

`merge_by_index` loops over the update in order, so it also handles a chunk that carries several fragments for the same call.

## Parsing the arguments

The arguments are a JSON string, and it's only valid once the call's last fragment has arrived. Merge the raw string while streaming, then validate it against the tool's argument model when the stream ends:

```python
from pydantic import BaseModel

class WeatherArgs(BaseModel):
    city: str


arguments = '{"city": ' + '"Paris"}'

print(WeatherArgs.model_validate_json(arguments))
#> city='Paris'
```

If you want to show the arguments while they stream in, parse the string accumulated so far after each merge with `pydantic_core.from_json(arguments, allow_partial=True)`. Keep that as a separate step that reads the merged state. A reducer that parsed fragments would see JSON split at arbitrary points.

## Token usage

Providers don't send usage the same way, so check yours before choosing a reducer:

- OpenAI sends usage once, in the last chunk, when you ask for it with `stream_options={"include_usage": True}`. Earlier chunks have `"usage": null`, so `last_non_null` keeps the final value.
- Anthropic's `message_delta` events carry running totals, not increments. Replace each count with the newest value. Adding them would count tokens twice.

Use `operator.add` on usage only when you're combining separate calls, as in [Agent state](agent-state.md#token-usage), not chunks of the same call.

## Performance

`merge` returns a new model for every chunk, so folding a long stream copies the message once per chunk. That's fine for a typical response of a few hundred chunks. For long outputs where it shows up in a profile, merge batches of chunks instead, or keep the text in a list and join it once at the end.
