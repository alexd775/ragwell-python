# Handle errors and resume work

Catch `RagwellError` for SDK failures. `ApiError` adds `status_code`, stable `code`, `request_id`, `operation_id`, and safe details. Log those fields and relevant resource IDs. Do not log API keys, document contents, queries, signed URLs, or raw HTTP bodies.

```python
from pathlib import Path

from ragwell import ApiError, RagwellError, WaitTimeoutError

try:
    ready = await project.documents.upload_and_wait(
        file=Path("guide.md"), wait_timeout=300
    )
except WaitTimeoutError as exc:
    print("Observation timed out; job:", exc.identifiers.get("job_id"))
except ApiError as exc:
    print(exc.status_code, exc.code, exc.request_id)
except RagwellError as exc:
    print(type(exc).__name__, exc.identifiers.get("upload_id"))
```

Keep `error.identifiers` private: it can include an idempotency key. The accepted upload's `job_id` and other IDs survive later `upload_and_wait()` failures in `exc.identifiers`. Resume with `jobs.get(job_id)` or `jobs.wait(job_id)`. A wait timeout or cancelled Python task does not cancel the server job. `OperationFailedError` means a waiter observed a terminal failure; decide explicitly whether `jobs.retry()` or `deletions.retry()` is appropriate.

For a lost create response, retry only the **same logical command** with its original idempotency key and identical payload, within the API's receipt window. Do not invent a new key to recover an uncertain upload. The SDK uses bounded retries for safe reads and replayable commands. Search is never automatically replayed. Validation, permission, quota, and revision conflicts need a changed request or grant rather than a blind retry.

See [error types](../reference/errors.md) and [deadlines and recovery](../reliability.md) for exact budgets and limits. The [troubleshooting guide](../help/troubleshooting.md) covers common causes.
