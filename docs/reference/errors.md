# Errors

All SDK failures derive from `RagwellError`. API responses with non-success status raise `ApiError` or a subclass. These provide safe `status_code`, `code`, `operation_id`, `request_id`, field errors, optional quota information, and retry hints where present.

| Error | Meaning |
|---|---|
| `ConfigurationError` | Missing or unsafe endpoint/key configuration |
| `AuthenticationError` | Invalid, expired, or revoked Ragwell key |
| `PermissionDeniedError` | Missing scope or current project/resource grant |
| `NotFoundError` | Resource absent or deliberately undisclosed |
| `ConflictError` | Current state, revision, or idempotency conflict |
| `ValidationError` | Request failed server validation |
| `RateLimitError` | Temporary rate/admission limit |
| `QuotaExceededError` | Fixed plan quota; do not blindly retry |
| `ServerError` | API or upstream failure |
| `TransportError` / `TransportTimeout` | HTTP boundary or deadline failure |
| `ProtocolError` | Response incompatible with the reviewed contract |
| `WaitTimeoutError` | Local observation ended; remote work may continue |
| `OperationFailedError` | Waiter observed a terminal failure |
| `PaginationError` | Unsafe repeated/invalid pagination cursor |
| `DownloadIntegrityError` | Export part failed size or SHA-256 check |

An error after upload acceptance may include `error.identifiers` with project, upload, document, version, and job IDs. Preserve them for diagnosis and resuming observation. Do not log credentials, query text, source content, or raw response bodies. See [errors and recovery](../guides/errors-and-recovery.md) for examples and [troubleshooting](../help/troubleshooting.md) for common fixes.
