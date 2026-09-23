# Upload documents and observe processing

For one file, `documents.upload()` returns accepted intake IDs immediately. `documents.upload_and_wait()` also observes its processing job. These helpers accept paths, bytes, and seekable binary streams. Bytes and streams need an explicit filename. Check the live `client.upload_policy.get()` for accepted formats and limits.

```python
from pathlib import Path

from ragwell import AsyncRagwell

async with AsyncRagwell(base_url=base_url, api_key=api_key) as client:
    project = client.project(project_id)
    intake = await project.documents.upload(file=Path("guide.md"))
    print(intake.document.id, intake.job_id)
    job = await project.jobs.wait(intake.job_id, timeout=300)
    print(job.status)
```

A wait timeout stops observation; the accepted upload may keep processing. Retain `intake.job_id` and inspect or wait again. On an ambiguous transfer, use the IDs attached to the SDK error and the original idempotency key instead of creating a second logical upload. See [error recovery](errors-and-recovery.md).

The SDK does not provide a folder-sync API. The [async example project](../../examples/async_project/README.md) has a small script that scans a local folder, skips files whose **exact filename** exists remotely, uploads the rest sequentially, and reports status. It does not compare file contents, update matching names, or delete remote files. Use that policy only if it fits your application. The project list can be paged through `documents.iter()`.

For document state and job details, use `documents.get(document_id)`, `documents.inspect(document_id)`, and `jobs.get(job_id)`. A successful job and a searchable document are separate observable facts; the [lifecycle](../concepts/document-lifecycle.md) explains them.
