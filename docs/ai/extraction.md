# Structured extraction

A document too long for one prompt is split into chunks, and the model extracts a structured record from each one. Each record is partial: a person mentioned in one chunk, a date found in another. Merging the records builds the result for the whole document.

## Merging records from chunks

Validate each chunk's output as a Pydantic model, then fold the records together. Entities are matched by name and merged, so a person found in two chunks appears once, with the roles from both:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge, reduce
from pydantic import BaseModel, field_validator

def merge_by_name(current: list, new: list) -> list:
    entities = {entity.name: entity for entity in current}
    for entity in new:
        entities[entity.name] = merge(entities[entity.name], entity) if entity.name in entities else entity
    return list(entities.values())


class Person(BaseModel):
    name: str
    roles: Annotated[set[str], Reducer(operator.or_)] = set()

    @field_validator("name")
    @classmethod
    def normalize(cls, name: str) -> str:
        return " ".join(name.split()).title()


class Extraction(BaseModel):
    people: Annotated[list[Person], Reducer(merge_by_name)] = []
    topics: Annotated[set[str], Reducer(operator.or_)] = set()


chunk_outputs = [
    '{"people": [{"name": "ada lovelace", "roles": ["author"]}], "topics": ["engines"]}',
    '{"people": [{"name": "Charles  Babbage", "roles": ["inventor"]}]}',
    '{"people": [{"name": "Ada Lovelace", "roles": ["mathematician"]}], "topics": ["algorithms"]}',
]

result = reduce(Extraction(), (Extraction.model_validate_json(output) for output in chunk_outputs))

for person in result.people:
    print(person.name, sorted(person.roles))
#> Ada Lovelace ['author', 'mathematician']
#> Charles Babbage ['inventor']
print(sorted(result.topics))
#> ['algorithms', 'engines']
```

The validator normalizes each name as it's parsed, before any merging, so `"ada lovelace"` and `"Ada Lovelace"` share a key. Normalize keys at the boundary like this. A reducer only sees the values it's given.

Deduplicating with `set()` on whole records doesn't work for this. Two records for the same person with different roles are different values, so both would be kept.

## Filling gaps with follow-up calls

Sometimes one pass leaves fields empty, and you ask the model again for only what's missing. Because a validated Pydantic model only sets the fields that were in the output, the follow-up answer fills in the gaps without clearing what you already have:

```python
from anymerge import merge
from pydantic import BaseModel

class Invoice(BaseModel):
    number: str | None = None
    total: float | None = None
    due_date: str | None = None


first_pass = Invoice.model_validate_json('{"number": "INV-7", "total": 120.5}')
follow_up = Invoice.model_validate_json('{"due_date": "2026-12-01"}')

print(merge(first_pass, follow_up))
#> number='INV-7' total=120.5 due_date='2026-12-01'
```

`first_pass.model_copy(update=follow_up.model_dump())` would set `number` and `total` back to `None`, because `model_dump` includes every field.

## Order of chunks

Chunks are often processed in parallel. `operator.add`, `operator.or_`, `max` and `min` give the same result in any order, so fields that use them don't depend on which chunk finishes first. A field without a reducer keeps the last chunk's value, and `merge_by_name` above lists entities in the order they were first seen. If those need to be stable, apply the records in chunk order with `reduce`.
