# Ragwell Python SDK

Typed synchronous and asynchronous Python clients for Ragwell, a managed service
for document ingestion and retrieval with source citations.

**Status: `0.2.0` developer beta.** The release implements the reviewed machine API,
including optional Jev reranking, and is published on
[PyPI](https://pypi.org/project/ragwell/0.2.0/). Its public wheel passed clean
installation and the deployed beta lifecycle. The SDK returns retrieval evidence
and citations; it does not generate answers.

New to Ragwell? Start with the [Python SDK quickstart](docs/quickstart.md) or browse
[the documentation](docs/index.md). The [runnable async project](examples/async_project/README.md)
uses the published package from PyPI.

## Requirements and installation

Python 3.11 or newer is required. Install the `ragwell` distribution from PyPI:

```sh
python -m pip install ragwell
```

For local development:

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

## Optional reranking (`0.2.0`)

After a project owner configures their paid Jev key in the dashboard, request
reranking for an individual search. This interface requires `ragwell>=0.2.0`:

```python
from ragwell import Ragwell
from ragwell.types import RerankRequest

with Ragwell() as client:
    result = client.project(project_id).search(
        query="What is the refund window?",
        k=5,
        rerank=RerankRequest(id="jev"),
    )
    for item in result.items:
        print(item.scores.rerank, item.content)
```

`AsyncRagwell` exposes the same argument on `await project.search(...)`.
Omitting `rerank` or passing `None` uses ordinary retrieval. A missing project key
raises `ConflictError` with code `project_reranker_misconfigured`. Provider failures
remain explicit, and the SDK never automatically retries a search. Jev charges
the configured TypeSafe, OpenRouter or Vercel AI Gateway account. The client API
key is your **Ragwell** key; never pass the provider key as a search parameter.
Provider, API base URL and Jev model are project settings; the Ragwell SDK request
stays the same for every route.
`response.rerank` includes the provider, requested model and `resolved_model`
(null when no scoring ran), so gateway model aliases remain traceable.

Relevance is 0–3; `rerank_confidence` is separate on 0–1. Original source parts,
text/vector scores and `hybrid` score remain available; `scores.final` follows the
reranking order. The first version accepts no tuning parameters.

## Runnable async example

The [Python 3.12 example project](examples/async_project/README.md) installs the
published SDK from PyPI. Copy its `env.example` to `.env`, configure your project,
then run its scripts to sync a local document folder, retrieve to terminal/JSON,
optionally rerank with Jev, and clean the project.

## Development and qualification

```sh
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy
uv run --locked python scripts/generate.py --check
uv run --locked pytest
uv run --locked python -m build --no-isolation
```

The vendored artifact is `2026-09-22.1`, machine SHA-256
`edd7aa3d26def4a1dcafceee4af2b9d4ae5a0d2affde52719ce03e904cc5a509`.
See [contract provenance](contracts/README.md),
[generation qualification](docs/generation.md), and
[operation mapping](contracts/operations.json). Ordinary tests require no service,
credentials, provider calls, private repository, or model downloads.

The current contract adds optional Jev reranking. The published `0.2.0` wheel passed
the deployed beta lifecycle with the matching live contract, and its package runtime
passed a bounded synthetic Jev request. Representative quality, latency and cost
evaluation remains separate product-rollout work. The
[release record](docs/releasing.md) identifies the immutable artifacts and checks.

An optional [beta lifecycle validation](docs/beta-validation.md) checks the installed
wheel against a dedicated existing beta project with a scoped key. It starts no
services and is separate from the full fixture matrix and ordinary offline CI.

Documentation: [SDK docs](docs/index.md), [API reference and scopes](docs/reference/client-and-resources.md),
[sync lifecycle example](examples/sync_lifecycle.py),
[async lifecycle example](examples/async_lifecycle.py),
[compatibility and support](docs/help/compatibility.md), [security policy](SECURITY.md),
[changelog](CHANGELOG.md), [release runbook](docs/release-runbook.md), and
[release preparation](docs/releasing.md).

## License

[MIT](LICENSE).
