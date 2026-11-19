# Evaluation results

Large eval runs are split into shards that run in parallel, on different workers or on different days. Each shard produces a summary, and the summaries have to be combined into one report. Re-running a failed case should replace its old result, not count it twice.

```python
import operator
from typing import Annotated

from anymerge import Reducer, reduce
from anymerge.reducers import merge_by_key
from pydantic import BaseModel, Field

class CaseResult(BaseModel):
    case_id: str
    passed: bool
    score: Annotated[float, Field(ge=0, le=1)]
    latency_ms: Annotated[int, Field(ge=0)]


class Report(BaseModel):
    cases: Annotated[list[CaseResult], Reducer(merge_by_key("case_id"))] = []
    max_latency_ms: Annotated[int, Reducer(max)] = 0
    input_tokens: Annotated[int, Reducer(operator.add)] = 0

    @property
    def pass_rate(self) -> float:
        return sum(case.passed for case in self.cases) / len(self.cases)

    @property
    def mean_score(self) -> float:
        return sum(case.score for case in self.cases) / len(self.cases)


def shard(results: list[CaseResult], input_tokens: int) -> Report:
    return Report(
        cases=results,
        max_latency_ms=max(result.latency_ms for result in results),
        input_tokens=input_tokens,
    )


shard_1 = shard([
    CaseResult(case_id="q1", passed=True, score=1.0, latency_ms=820),
    CaseResult(case_id="q2", passed=False, score=0.2, latency_ms=4100),
], input_tokens=3000)
shard_2 = shard([CaseResult(case_id="q3", passed=True, score=0.8, latency_ms=950)], input_tokens=1400)
rerun = shard([CaseResult(case_id="q2", passed=True, score=0.9, latency_ms=1300)], input_tokens=1500)

report = reduce(Report(), [shard_1, shard_2, rerun])
print(len(report.cases), report.pass_rate, round(report.mean_score, 2))
#> 3 1.0 0.9
print(report.max_latency_ms, report.input_tokens)
#> 4100 5900
```

- `cases` uses `merge_by_key("case_id")`, so the re-run of `q2` replaces its failed result in place. Apply shards in the order they ran, so the newest result for a case wins.
- `max_latency_ms` and `input_tokens` give the same result in any order.
- `max_latency_ms` keeps the slowest latency of every run, including the one that was replaced. Recompute it from `cases` if it should only count the latest results.

## Averages

A mean can't be merged directly: the mean of two shards' means is wrong when the shards have different sizes. Keep the values a mean is built from, either the per-case results as above or a running sum and count, and compute the mean after merging:

```python
import operator
from typing import Annotated

from anymerge import Reducer, reduce
from pydantic import BaseModel

class ScoreTotals(BaseModel):
    count: Annotated[int, Reducer(operator.add)] = 0
    score_sum: Annotated[float, Reducer(operator.add)] = 0.0

    @property
    def mean(self) -> float:
        return self.score_sum / self.count


totals = reduce(ScoreTotals(), [ScoreTotals(count=3, score_sum=2.4), ScoreTotals(count=1, score_sum=0.2)])
print(totals.mean)
#> 0.65
```

The average of the two shards' means would be `(0.8 + 0.2) / 2 = 0.5`, which weighs the one-case shard as heavily as the three-case shard. The same applies to standard deviations and percentiles: merge what they're computed from, and compute them at the end.
