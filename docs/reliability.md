# Deadlines, response bounds and recovery

The client uses a monotonic budget for each ordinary request (30 seconds by default),
each complete `documents.upload()` (300 seconds), and each export-part stream or
save (300 seconds). Upload preparation/hashing and all three upload steps share
that transfer budget. `upload_and_wait()` starts a separate wait budget after the
intake is accepted. The three waiters default to 300 seconds.

Retries, socket operations, response decoding and polling consume the remaining
budget. A poll cannot start at its deadline or return a late success. An expired
wait raises `WaitTimeoutError`; a shorter request or transport timeout remains
`TransportTimeout`. `timeout=0` on a waiter immediately raises without a GET.
Timeouts must be finite; operation/transfer timeouts and polling intervals must also
be positive. Invalid upload-and-wait settings fail before starting an upload.

The default synchronous HTTPX adapter uses HTTPCore's public network-backend API
to recalculate the remaining timeout before socket reads/writes, including header
reads. Async HTTP sends and stream reads also use asyncio cancellation deadlines.
The adapter retains HTTP(S) environment proxy selection, TLS verification and
HTTPX's connection limits. HTTPCore is now a direct dependency (it was already an
HTTPX dependency); no generated code or API contract changed.

Blocking OS DNS/file operations, caller-provided streams and injected HTTPX
clients/transports must cooperate with timeouts: Python cannot safely interrupt
arbitrary synchronous user code. The SDK checks the budget before and after these
operations and rejects late completion. Async file operations run off the event
loop; on cancellation the SDK joins the in-flight file operation before restoring
or closing its handle. Cleanup can therefore take longer than the work budget.
Cancellation remains `asyncio.CancelledError` and never sends a remote cancel.

Safe reads and explicitly replayable commands retain at most two retries. Command
retries additionally stop before the 24-hour receipt horizon, even with a larger
configured timeout. `Retry-After` must be finite and fit the remaining budget.
Explicit reuse of a key from an earlier process still requires the caller to
respect the server's receipt lifetime; the SDK has no persistent receipt clock.
Searches are not automatically replayed.

Responses are streamed before parsing: successful JSON is capped at 16 MiB and
error bodies at 1 MiB of decoded bytes. `Content-Length` is not trusted as the
bound. Identity, gzip and deflate responses use decoding buffers of at most 64 KiB;
unsupported encodings fail safely. The cap is checked before appending the next
buffer. Raw buffers supplied by an injected transport are owned by that transport;
the SDK cannot prevent it from pre-buffering a response.

Export saves reject a chunk that would exceed the manifest size before writing
it, then verify exact size and SHA-256 before replacement. Failed or cancelled
saves remove SDK-owned temporary files and preserve an existing destination.
`stream_part()` has a transfer deadline but no manifest argument; callers own the
stream and should consume it inside `with` / `async with`. Iterator chunks are
at most the requested size and at most 64 KiB; they need not fill that size.

After an intake has been accepted, every subsequent SDK error from
`upload_and_wait()` retains `project_id`, `upload_id`, `document_id`, `version_id`
and `job_id` in `error.identifiers`, including forbidden job reads. The original
exception type and request correlation remain intact. These IDs support explicit
inspection/resumed waiting; the SDK never creates a replacement intake implicitly.
Protocol/transport errors use safe messages and suppress raw exception chains in
ordinary tracebacks. Raw response bodies, decoding values and transport URLs do
not appear in their string or representation.

`tests/test_reliability.py` contains the deterministic sync/async regressions,
including mock socket reads, compressed limits, all waiters, accepted-ID failures,
cancellation and temporary-file cleanup. These tests complement the existing
26-operation and installed-distribution tests; real-service qualification remains
a separate gate.

Design references: [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/),
[HTTPCore network backends](https://www.encode.io/httpcore/network-backends/).
