# Use the async client in an application

Use `AsyncRagwell` for asyncio applications and scripts. Create it once for the lifetime of an application component, share it within the same event loop, and close it at shutdown. A project handle is local and can be retained alongside the client.

```python
import os

from ragwell import AsyncRagwell


async def run_search(query: str) -> None:
    async with AsyncRagwell() as client:
        project = client.project(os.environ["RAGWELL_PROJECT_ID"])
        response = await project.search(query=query, k=5)
        for item in response.items:
            print(item.source_filename, item.content)
```

For a long-running application, hold the client in its startup/shutdown lifecycle instead of opening a new connection pool for every request. Use `await client.aclose()` if your framework does not support an async context manager around that lifecycle. SDK-created HTTP clients are closed by the SDK. An injected `httpx.AsyncClient` remains caller-owned unless you set `owns_http_client=True`.

Async iterators use `async for`:

```python
async for document in project.documents.iter(limit=50):
    print(document.id, document.state)
```

Task cancellation propagates as `asyncio.CancelledError`. It does not cancel accepted remote jobs, exports, or deletions. Save resource IDs if your application needs to resume observation. See [errors and recovery](errors-and-recovery.md) and [configuration](../reference/configuration.md). The [runnable async project](../../examples/async_project/README.md) uses only the published PyPI package.
