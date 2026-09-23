# Client configuration

`Ragwell` and `AsyncRagwell` take the same configuration. Pass `base_url` and `api_key` explicitly or set `RAGWELL_BASE_URL` and `RAGWELL_API_KEY`; explicit arguments win. The URL is the API origin without `/v1`. The SDK does not load `.env` files or choose an environment for you.

```python
from ragwell import AsyncRagwell

async with AsyncRagwell(
    base_url="https://api-beta.ragwell.dev",
    api_key=api_key,
    operation_timeout=30,
    transfer_timeout=300,
) as client:
    project = client.project(project_id)
```

| Setting | Default | Applies to |
|---|---:|---|
| `operation_timeout` | 30 seconds | Ordinary requests |
| `transfer_timeout` | 300 seconds | Complete upload and export-part transfer |
| Waiter `timeout` | 300 seconds | Job, deletion, and export observation |
| `verify` | `True` | TLS verification for SDK-created HTTP clients |

Timeouts are finite. Upload hashing and all transfer steps share the transfer budget. `upload_and_wait()` starts a separate wait budget after acceptance. Redirects are not followed. A `transport` and `http_client` cannot be supplied together.

Use a context manager or close the client explicitly. Injected HTTPX clients are caller-owned unless `owns_http_client=True`; an SDK-created client is SDK-owned. Keep an async client in one event loop. See [async applications](../guides/async-applications.md) and [deadline details](../reliability.md).

Safe reads have at most two bounded retries. Replayable commands retain one idempotency key for the logical command; search is never automatically replayed. The [recovery guide](../guides/errors-and-recovery.md) explains what to do when a response is lost.
