# Ragwell Python SDK

Typed synchronous and asynchronous Python clients for Ragwell, a managed service
for document ingestion and retrieval with source citations.

**Status: development SDK (`0.1.0.dev0`).** The complete reviewed machine API is
implemented and qualified from an installed wheel against an isolated local HTTP
service. The package is unpublished; its Linux, macOS and Windows CI matrix passes.
The SDK returns retrieval
evidence and citations; it does not generate answers.

## Requirements and installation

Python 3.11 or newer is required. The planned distribution name is `ragwell`, but
PyPI ownership and publication have not been completed. For local development:

```sh
uv sync --locked --python 3.11
```

Runtime use requires an existing project grant and API key. The SDK does not create
projects, users, keys, or billing resources. Supply the endpoint and key explicitly
or through `RAGWELL_BASE_URL` and `RAGWELL_API_KEY`; explicit arguments win. No beta
hostname is built into the package and no `.env` file is loaded implicitly.

## Synchronous quick start

```python
import os
from pathlib import Path

from ragwell import Ragwell
from ragwell.types import SearchFilters

with Ragwell() as client:
    project = client.project(os.environ["RAGWELL_PROJECT_ID"])
    ready = project.documents.upload_and_wait(
        file=Path("guide.pdf"),
        wait_timeout=300,
    )
    results = project.search(
        query="What is the retention policy?",
        filters=SearchFilters(document_ids=[ready.intake.document.id]),
    )
    for item in results.items:
        print(item.rank, item.source_filename, item.parts)
```

## Asynchronous quick start

```python
import os

from ragwell import AsyncRagwell


async def retrieve(query: str):
    async with AsyncRagwell() as client:
        project = client.project(os.environ["RAGWELL_PROJECT_ID"])
        return await project.search(query=query)
```

Initialize one async client at application startup, share it within its owning event
loop, and close it at shutdown. Injected HTTPX clients are borrowed unless
`owns_http_client=True`; SDK-created pools are owned and closed by the SDK.

## Public resource layout

`client.project(project_id)` is local and performs no preflight request. Both client
styles expose the same 26 contract operations:

- `client.upload_policy.get()`
- `project.get()` and `project.embedding_connection.get()`
- `project.uploads.create()`, `.get()`, `.upload_content()`, and `.finalize()`
- `project.documents.list()`, `.get()`, `.replace_metadata()`, `.delete()`,
  `.inspect()`, and `.activity()`
- `project.documents.generations.list()`, `.chunks.list()`, and `.sources.get()`
- `project.documents.exports.create()`, `.get()`, `.stream_part()`, and
  `.download_part()`
- `project.jobs.list()`, `.get()`, `.retry()`, and `.cancel()`
- `project.deletions.get()` and `.retry()`
- `project.search()`

Convenience workflows add `documents.upload()`, `documents.upload_and_wait()`,
`jobs.wait()`, `deletions.wait()`, `documents.exports.wait()`, and lazy `.iter()`
methods for documents, jobs, generations, and chunks.

Generated public types and enums are available from `ragwell.types`. They preserve
UUIDs, aware timestamps, omission through `UNSET`, explicit null, complete source
parts and scores, command acceptance versus current resource state, and additive
response fields through `additional_properties`.

## Reliability and ownership

- HTTP 202 means accepted, never completed. Waiters have finite deadlines and never
  cancel or retry remote work implicitly.
- Job cursors are opaque and filter/project scoped. Iterators never parse or create
  them, stop at null, and reject repeated cursors.
- Safe reads receive at most two bounded retries. Replayed mutations keep one
  idempotency key for the logical command. Search is never automatically replayed.
- `command_in_progress` may retry within the deadline using `Retry-After`; quota,
  authorization, validation, and revision/idempotency conflicts do not.
- Upload helpers accept paths, bytes, and seekable binary streams, hash incrementally,
  restore caller cursors, and never close caller-owned streams. Bytes/streams need
  an explicit filename.
- Export saves stream to an SDK-owned temporary file in the destination directory,
  verifies manifest byte size and SHA-256, then replaces atomically. Overwrite is
  opt-in.

See [deadlines, bounds and recovery](docs/reliability.md) for timeout-zero behavior,
transfer budgets, cancellation, decoded-body caps and accepted-intake recovery IDs.

Errors derive from `RagwellError`. `ApiError` preserves safe status/code, field
errors, quota detail, retry hints, operation ID, and server `X-Request-ID`. Transport,
protocol, wait-timeout, terminal-operation, pagination, and integrity failures are
distinct. Exceptions do not include keys, request bodies, queries, raw HTML, or
document content.

## Development and qualification

```sh
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy
uv run --locked python scripts/generate.py --check
uv run --locked pytest
uv run --locked python -m build --no-isolation
```

The vendored artifact is `2026-09-19.1`, machine SHA-256
`8e05de4ae0f3aa76261e97ad07be1fc77756f317c3e2c20ab2be3efb2cb6db90`.
See [contract provenance](contracts/README.md),
[generation qualification](docs/generation.md), and
[operation mapping](contracts/operations.json). Ordinary tests require no service,
credentials, provider calls, private repository, or model downloads.

The reviewed artifact is available in the public repository. Local installed-wheel HTTP qualification
is recorded in [HTTP qualification](docs/http-qualification.md). Package ownership,
protected TestPyPI/PyPI publication and service availability remain release gates.

An optional [beta lifecycle validation](docs/beta-validation.md) checks the installed
wheel against a dedicated existing beta project with a scoped key. It starts no
services and is separate from the full fixture matrix and ordinary offline CI.

Documentation: [API reference and scopes](docs/api-reference.md),
[sync lifecycle example](examples/sync_lifecycle.py),
[async lifecycle example](examples/async_lifecycle.py),
[compatibility and support](docs/compatibility.md), [security policy](SECURITY.md),
[changelog](CHANGELOG.md), and [release preparation](docs/releasing.md).

## License

[MIT](LICENSE).
