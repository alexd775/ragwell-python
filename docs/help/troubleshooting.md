# Troubleshooting

Start with the exception's class, safe error code, request ID, and retained resource IDs. Use a synthetic reproduction when reporting a problem; do not share keys, document content, queries, or raw responses.

| Symptom | Check |
|---|---|
| Configuration error | Supply `RAGWELL_BASE_URL` and `RAGWELL_API_KEY` or explicit arguments. Use the origin without `/v1`. |
| 401 authentication | Confirm the Ragwell key is current and is being sent to the intended environment. |
| 403 permission | Check both the operation scope and the key's current grant to this project. See [scopes](../reference/scopes.md). |
| Upload returns IDs but search is empty | An accepted intake may still be processing. Inspect the job and document; confirm the job succeeded and the document is searchable. |
| Wait timeout | Remote work may continue. Save `error.identifiers`; resume with `jobs.get()/wait()`, `deletions.get()/wait()`, or export equivalents. |
| Upload outcome is uncertain | Reuse the original idempotency key and identical payload within the API receipt window, or inspect the retained upload ID. |
| 409 conflict | Check metadata revision, idempotency payload, current resource state, or missing reranker configuration according to `error.code`. |
| Quota or rate error | A fixed quota needs a plan/usage change; a temporary rate limit may include a retry hint. |
| Reranking fails | Verify the project owner configured and funded Jev in the dashboard. The SDK does not silently fall back. |
| Export download fails | Check the export state and expiry; an integrity failure leaves the prior destination intact. |
| Async client fails across loops | Create/use it in its owning asyncio event loop and close it at shutdown. |

The [error reference](../reference/errors.md) identifies exception classes; [recovery](../guides/errors-and-recovery.md) covers accepted work and retries. For support, include the SDK and Python versions, safe error class/code/request ID, and a minimal synthetic example via [GitHub issues](https://github.com/alexd775/ragwell-python/issues). Follow [SECURITY.md](../../SECURITY.md) for confidential reports.
