# Projects, API keys, and scopes

A project is the boundary for documents and retrieval. Create and administer projects in the Ragwell dashboard. The Python SDK uses an existing project and cannot create projects, users, keys, grants, or billing resources.

Create a Ragwell API key in the dashboard and grant it to the intended project. The key needs the scope required by each operation. A scope alone does not grant access to every project; the project's current server-side grant also applies. See the [scope table](../reference/scopes.md).

The SDK uses two inputs for each request:

- `RAGWELL_BASE_URL`: the API **origin**, without `/v1` or a project path.
- `RAGWELL_API_KEY`: a Ragwell API key, kept in environment or secret storage.

Pass the project UUID to `client.project(project_id)`. This creates a local handle; it does not check the project or make a network call. The first operation enforces the key's current grant.

```python
from ragwell import Ragwell

with Ragwell(base_url=base_url, api_key=api_key) as client:
    project = client.project(project_id)
    details = project.get()  # Requires project:read.
```

A provider key for embeddings or optional Jev reranking is a separate project setting managed in the dashboard. Never pass a provider credential as the Ragwell API key or as a search argument. See [configuration](../reference/configuration.md) and [optional reranking](../guides/reranking.md).
