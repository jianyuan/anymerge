# Retrieval

Retrieval-augmented generation often runs more than one search: a keyword and a vector search, or several rewrites of the same question. Their results overlap, so before you build the prompt you merge them into one list with each document appearing once.

## Deduplicating documents

[`merge_by_key`](../guide/lists.md) matches documents by ID, but it replaces a matched document with the new one, which would keep whichever retriever ran last. Write a reducer that merges matched documents instead, so the document model's own reducers decide what to keep. Here a duplicate keeps its highest score and the names of every retriever that found it:

```python
import operator
from typing import Annotated

from anymerge import Reducer, merge, reduce
from pydantic import BaseModel, Field

def merge_by_id(current: list, new: list) -> list:
    docs = {doc.id: doc for doc in current}
    for doc in new:
        docs[doc.id] = merge(docs[doc.id], doc) if doc.id in docs else doc
    return sorted(docs.values(), key=lambda doc: doc.score, reverse=True)


class Document(BaseModel):
    id: str
    text: str
    score: Annotated[float, Reducer(max), Field(ge=0, le=1)]
    found_by: Annotated[set[str], Reducer(operator.or_)] = set()


class Results(BaseModel):
    documents: Annotated[list[Document], Reducer(merge_by_id)] = []


keyword = Results(documents=[
    Document(id="a", text="Reducers fold values", score=0.4, found_by={"keyword"}),
    Document(id="b", text="Merging models", score=0.7, found_by={"keyword"}),
])
vector = Results(documents=[
    Document(id="a", text="Reducers fold values", score=0.9, found_by={"vector"}),
    Document(id="c", text="Typed state", score=0.5, found_by={"vector"}),
])

for doc in reduce(Results(), [keyword, vector]).documents:
    print(doc.id, doc.score, sorted(doc.found_by))
#> a 0.9 ['keyword', 'vector']
#> b 0.7 ['keyword']
#> c 0.5 ['vector']
```

The `Field(ge=0, le=1)` constraint rejects a document whose score isn't normalized when the retriever's output is validated, which catches a retriever that returns raw distances. Scores from different retrievers are only comparable when they're on the same scale.

## Reciprocal rank fusion

When scores aren't comparable, reciprocal rank fusion ranks documents by position instead. Each list gives a document `1 / (k + rank)`, and a document's fused score is the sum over every list it appears in. Turn each list into per-document contributions first, then let a reducer that sums a dict keyed by document ID do the fusion:

```python
from typing import Annotated

from anymerge import Reducer, reduce
from pydantic import BaseModel

def add_scores(current: dict[str, float], new: dict[str, float]) -> dict[str, float]:
    return {key: current.get(key, 0) + new.get(key, 0) for key in current | new}


class Fusion(BaseModel):
    scores: Annotated[dict[str, float], Reducer(add_scores)] = {}


def rrf(ranked_ids: list[str], k: int = 60) -> Fusion:
    return Fusion(scores={doc_id: 1 / (k + rank) for rank, doc_id in enumerate(ranked_ids, 1)})


keyword = ["b", "a", "d"]
vector = ["a", "c", "b"]

fused = reduce(Fusion(), [rrf(keyword), rrf(vector)])
print(sorted(fused.scores, key=fused.scores.get, reverse=True))
#> ['a', 'b', 'c', 'd']
```

Addition gives the same result in any order, so you can fuse each retriever's results as soon as it finishes.
