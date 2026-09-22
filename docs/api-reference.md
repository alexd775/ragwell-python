# Python SDK reference

This reference describes the maintained `0.2.0` release-candidate interface. Both
`Ragwell` and `AsyncRagwell` expose the same 26 machine operations. Examples below use a sync
`project = client.project(project_id)`; await equivalent async calls and use
`async for` for async iterators. The project handle is local and makes no request.
IDs accept `uuid.UUID` or UUID strings. Results and request models are imported
from `ragwell.types`; they support `to_dict()` / `from_dict()`.

## Configuration and ownership

```python
from ragwell import Ragwell

with Ragwell(
    base_url="https://api-beta.ragwell.dev",
    api_key=key,
    operation_timeout=30,
    transfer_timeout=300,
) as client:
    project = client.project(project_id)
```

Explicit arguments override `RAGWELL_BASE_URL` / `RAGWELL_API_KEY`. The beta URL is
required; use its origin without `/v1`. No `.env` file is loaded. TLS verification
is enabled and redirects are not followed. Use `with` / `async with`, or explicit
`close()` / `await aclose()`. Reuse async clients within their owning event loop.
An injected `http_client` remains caller-owned unless `owns_http_client=True`.
`transport` and `http_client` cannot both be supplied. Advanced injected transports
must cooperate with deadlines; see [reliability](reliability.md).

Projects, accounts, API keys, grants, billing and processing-profile administration
are prepared outside the SDK. A project's current server-side grant and each
operation's scope are both required. Constructing a handle does not require an
extra `project:read` permission.

## Operations and scopes

Arguments such as `document_id`, `generation_id`, `export_id`, `job_id` and
`receipt_id` below are returned by earlier operations; no tenant selector is accepted.

| Call | Result / purpose | Scope |
|---|---|---|
| `client.upload_policy.get()` | Allowed formats and intake limits | Public |
| `project.get()` | Project and processing profile | `project:read` |
| `project.embedding_connection.get()` | Project's current embedding connection | `project:read` |
| `project.uploads.create(request, idempotency_key=...)` | `UploadSessionResponse` from `CreateUploadRequest` | `document:upload` |
| `project.uploads.get(upload_id)` | Recover upload state and accepted IDs | `document:upload` |
| `project.uploads.upload_content(upload_id, content=..., content_type=..., content_length=...)` | Transfer bytes or binary stream | `document:upload` |
| `project.uploads.finalize(upload_id)` | `FinalizedIntakeResponse`; work accepted | `document:upload` |
| `project.documents.list(**filters)` | One `DocumentListResponse` page | `document:list` |
| `project.documents.get(document_id)` | `DocumentResponse` | `document:read` |
| `project.documents.replace_metadata(document_id, request, idempotency_key=...)` | Revision-checked replacement | `document:update` |
| `project.documents.delete(document_id, idempotency_key=...)` | Durable `DocumentDeletionResponse` | `document:delete` |
| `project.documents.inspect(document_id, generation_id=...)` | Processing/generation inspection | `document:read` |
| `project.documents.activity(document_id, generation_id=...)` | Measured retrieval activity | `document:read` |
| `project.documents.generations.list(document_id, after=..., limit=20)` | Generation page | `document:read` |
| `project.documents.chunks.list(document_id, generation_id, limit=25, after=..., text=..., source_ordinal=...)` | Chunk page | `document:read` |
| `project.documents.sources.get(document_id, generation_id, source_id, offset=0, limit=4000)` | Bounded source window | `document:read` |
| `project.documents.exports.create(document_id, request, idempotency_key=...)` | Accept `CreateDocumentExportRequest` | `document:read` |
| `project.documents.exports.get(document_id, export_id)` | Export state, parts, hashes and expiry | `document:read` |
| `project.documents.exports.stream_part(document_id, export_id, part_number)` | Context-managed byte stream | `document:read` |
| `project.jobs.list(**filters)` | One `IngestionJobListResponse` page | `job:list` |
| `project.jobs.get(job_id)` | Current durable job | `job:read` |
| `project.jobs.retry(job_id, idempotency_key=...)` | Explicit failed-job retry | `job:retry` |
| `project.jobs.cancel(job_id, idempotency_key=...)` | Explicit cancellation request | `job:cancel` |
| `project.search(query=..., filters=..., k=5)` | Ranked chunks and complete source provenance | `retrieval:search` |
| `project.deletions.get(receipt_id)` | Current deletion receipt | `deletion:read` |
| `project.deletions.retry(receipt_id, idempotency_key=...)` | Explicit failed-deletion retry | `deletion:retry` |

`documents.exports.download_part(document_id, export_id, part, destination,
overwrite=False)` wraps the same download operation, verifies the manifest's byte
size and SHA-256, and atomically installs the file. Supply the `part` model from the
export result. Streams alone do not have a manifest argument; consume them inside
`with` / `async with`. Inspection can omit job/deletion details without their scopes.

## Upload, processing and recovery

```python
from pathlib import Path

intake = project.documents.upload(file=Path("guide.txt"), idempotency_key=saved_key)
job = project.jobs.wait(intake.job_id, timeout=300)
# Or: ready = project.documents.upload_and_wait(file=Path("guide.txt"), wait_timeout=300)
# ready.intake retains the accepted identifiers; ready.job is the succeeded job.
```

`upload()` supports paths, bytes and seekable binary streams. Bytes/streams require
`filename`; optionally set `media_type`, `metadata=DocumentMetadataInput(...)` and
`tags`. Caller-owned streams remain open and their initial cursor is restored.
PDF, text and Markdown are subject to the live upload policy. Non-seekable streams
are rejected by the helper; the raw transfer operation requires known length.
`upload_and_wait()` additionally requires `job:read` and uses a separate wait budget.

A returned intake or HTTP 202 means accepted, not processed. For an ambiguous upload,
retain `RagwellError.identifiers`; inspect a known `uploads.get(upload_id)` or replay
the original create request with its original key. Do not start a new upload simply
because a response was lost. Keys must be reused with identical logical payloads
within the server's replay window. See [deadline and replay details](reliability.md).

## Pages, filters and metadata

Document/job lists accept `limit=50`, `document_ids`, `tags_any`, `tags_all`,
`source_any`, `author_any`, `language_any` and `category_any`. Jobs additionally accept
`status=[IngestionJobStatus.FAILED]`. Pass a page's `next_cursor` unchanged as `after`
and preserve the filters. Job cursors are opaque strings; document/generation
cursors are UUID-shaped and chunk cursors are integers. Do not construct cursors.

`documents.iter(**filters)`, `jobs.iter(**filters)`,
`documents.generations.iter(document_id, after=None, limit=20)` and
`documents.chunks.iter(document_id, generation_id, **filters)` traverse lazily and
raise `PaginationError` on repeated cursors. Use single-page methods when the
application owns pagination. Limits and filter combinations remain server-validated.

```python
from ragwell.types import DocumentMetadataInput, ReplaceDocumentMetadataRequest

current = project.documents.get(document_id)
updated = project.documents.replace_metadata(
    document_id,
    ReplaceDocumentMetadataRequest(
        expected_revision=current.metadata_revision,
        tags=["reference"],
        metadata=DocumentMetadataInput(source="handbook", language="en"),
    ),
)
```

This replaces metadata/tags; it is not a partial merge. A new command with a stale
revision conflicts. `UNSET` represents omission, distinct from an explicit `None`.
Use the documented request models; arbitrary dictionaries/reserved tenant filters
are not supported public inputs.

## Retrieval, exports and waiters

Use `SearchFilters(document_ids=[...], tags_all=[...], source_any=[...])` for bounded
retrieval. Hits retain document/version/chunk IDs, ranked scores, citation variants
and ordered `parts`, including source IDs and spans where available. The SDK returns
retrieval evidence, not generated answers. Preserve full parts when showing provenance.
Search is metered and is never automatically replayed.

```python
from pathlib import Path
from ragwell.types import CreateDocumentExportRequest

export = project.documents.exports.create(
    document_id,
    CreateDocumentExportRequest(
        generation_id=generation_id,
        include_embeddings=False,
    ),
)
export = project.documents.exports.wait(document_id, export.id, timeout=300)
for part in export.parts:
    project.documents.exports.download_part(
        document_id,
        export.id,
        part,
        Path(f"part-{part.part_number}.ndjson"),
    )
```

All waiters accept `timeout=300` and `initial_interval=1` by default:

| Waiter | Successful state | Terminal failure |
|---|---|---|
| `jobs.wait(job_id)` | `succeeded` | `failed`, `cancelled` |
| `deletions.wait(receipt_id)` | `completed` | `failed` |
| `documents.exports.wait(document_id, export_id)` | `succeeded` | `failed`, `expired` |

Timeout stops local observation; it does not cancel or retry remote work. Save IDs
and call the waiter again. Async cancellation propagates `asyncio.CancelledError`.
Retry/cancel methods are explicit commands and may require extra scopes; a local
wait timeout is not a reason to call them automatically. Unknown lifecycle enums
raise `ProtocolError` rather than becoming success or endless polling.

## Errors and examples

Catch `RagwellError` for SDK failures. `ApiError` preserves status/code, request ID,
field errors and quota detail; subclasses distinguish authentication, permissions,
not-found, conflicts, validation, rate limits, quota and server errors. Transport,
protocol, wait-timeout, failed-operation, pagination and download-integrity failures
are distinct. Record IDs and error classes for diagnosis; avoid response dumps,
queries, document contents, credentials and signed URLs.

The [sync lifecycle script](../examples/sync_lifecycle.py) and
[async lifecycle example](../examples/async_lifecycle.py) create only their synthetic
document, export it temporarily and delete it in `finally`. Their cleanup can still
fail if the API is unavailable; retain any error's recovery identifiers. The
[beta runner](beta-validation.md) adds durable reporting, upload recovery, wheel
identity and stricter integration assertions for release validation.


## Optional Jev reranking (`0.2.0`)

`project.search(query=..., k=5, rerank=RerankRequest(id="jev"))` and its async
counterpart use the existing `retrieval:search` scope. Import `RerankRequest` from
`ragwell.types`. Omit the argument or use `None` to skip reranking. `params` may be
omitted or `RerankParams()`; no provider-specific tuning is currently supported.
Project owners configure TypeSafe, OpenRouter or Vercel AI Gateway, API base URL,
Jev model ID and paid credentials in dashboard settings.
The SDK neither accepts nor administers provider credentials.

Results preserve all source identities and parts. `response.rerank` identifies
provider, requested model, resolved model, policy, configuration revision, candidate
count, and whether scoring ran. `resolved_model` is null when no scoring ran.
No candidates means `applied=False` and no provider call. Reranked `scores.final`
and `scores.rerank` are 0–3 relevance; `scores.hybrid` preserves the original ranking
score and `scores.rerank_confidence` is a distinct 0–1 confidence measure.

Missing project configuration returns `409 project_reranker_misconfigured`.
Unknown parameters fail validation. Provider error/deadline failures return typed
API errors; the SDK does not retry or silently fall back to ordinary retrieval.
