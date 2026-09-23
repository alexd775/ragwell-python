# Search and filter results

Search a project for relevant chunks. A result is evidence with provenance, not an answer written by Ragwell.

```python
from ragwell.types import SearchFilters

filters = SearchFilters(tags_all=["handbook"])
response = await project.search(
    query="Where are the purple lanterns?",
    filters=filters,
    k=5,
)
for hit in response.items:
    print(hit.rank, hit.source_filename, hit.content)
    print(hit.document_id, hit.document_version_id, hit.chunk_id)
    print(hit.citation, hit.parts)
```

You can filter by `document_ids`, `tags_any`, `tags_all`, `source_any`, `author_any`, `language_any`, and `category_any`. The server validates bounds and combinations. A query may return zero items. Preserve the full `parts` list when displaying or recording a citation; `citation` can be absent.

`k` defaults to 5. Search is metered and the SDK does not replay it automatically, even after a timeout or provider error. If your application chooses to repeat a search, it owns that decision and its cost. [Retrieval and citations](../concepts/retrieval-and-citations.md) explains result fields. [Optional reranking](reranking.md) describes the Jev request.
