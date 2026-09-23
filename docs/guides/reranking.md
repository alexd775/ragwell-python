# Optional Jev reranking

A project owner configures a paid Jev provider route and credential in the Ragwell dashboard. A search can then request reranking explicitly with `ragwell>=0.2.0`. The SDK does not accept or administer the provider key.

```python
from ragwell.types import RerankRequest

response = await project.search(
    query="What is the refund window?",
    k=5,
    rerank=RerankRequest(id="jev"),
)
for hit in response.items:
    print(hit.rank, hit.content, hit.scores.final, hit.scores.rerank)
```

Omit `rerank` or pass `None` for ordinary retrieval. Reranking can incur charges on the configured TypeSafe, OpenRouter, or Vercel AI Gateway account. It uses the existing `retrieval:search` scope and does not change source IDs or citation parts.

`response.rerank` records provider and model information, candidate count, and whether scoring ran. `scores.hybrid` retains the original retrieval score. When reranking runs, `scores.final` follows the new order and `scores.rerank` represents relevance on a 0–3 scale; `rerank_confidence` is a separate 0–1 value. Missing project configuration raises `409 project_reranker_misconfigured`. The SDK does not retry or silently fall back on provider failure.

See [retrieval and citations](../concepts/retrieval-and-citations.md) and the [async example's `--rerank` option](../../examples/async_project/README.md).
