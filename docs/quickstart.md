# Quickstart: upload and retrieve

This guide uses the published Python SDK and an existing Ragwell project. At the end, you will have one processed document and a search result with its source.

## 1. Prepare a project and key

In the Ragwell dashboard, create a project and a Ragwell API key granted to that project. The key needs `document:upload`, `job:read`, and `retrieval:search` for this guide. Copy the project UUID and API origin. Use the origin without `/v1`, for example `https://api-beta.ragwell.dev`.

Keep the key in your application's secret storage or environment. The SDK reads `RAGWELL_BASE_URL` and `RAGWELL_API_KEY`; it does not load a `.env` file by itself. See [projects and keys](concepts/projects-and-keys.md).

## 2. Install the package

Use Python 3.11 or newer in your own environment:

```sh
python -m pip install ragwell
```

Create a local UTF-8 file named `guide.txt` containing: `The purple lanterns are stored in the north cabinet.`

## 3. Run a small script

Set `RAGWELL_BASE_URL`, `RAGWELL_API_KEY`, and `RAGWELL_PROJECT_ID` in your environment, then save this as `quickstart.py`:

```python
import os
from pathlib import Path

from ragwell import Ragwell
from ragwell.types import SearchFilters

with Ragwell() as client:
    project = client.project(os.environ["RAGWELL_PROJECT_ID"])
    ready = project.documents.upload_and_wait(
        file=Path("guide.txt"),
        wait_timeout=300,
    )
    result = project.search(
        query="Where are the purple lanterns?",
        filters=SearchFilters(document_ids=[ready.intake.document.id]),
    )
    for hit in result.items:
        print(hit.source_filename, hit.content)
        print("Citation:", hit.citation)
        print("Source parts:", hit.parts)
```

Run `python quickstart.py`. If processing takes longer than 300 seconds, the local wait ends while the remote job may continue. Save the IDs on the error and resume observation; see [errors and recovery](guides/errors-and-recovery.md). Search may return no hits if the document is not searchable or the query finds no matching chunk.

The result contains retrieved text and provenance, not a generated answer. The [retrieval guide](concepts/retrieval-and-citations.md) explains how to use source parts and scores.

## Next

The [async example project](../examples/async_project/README.md) offers three terminal scripts to sync a local folder, retrieve JSON, and clean a dedicated project. [Upload and sync](guides/upload-and-sync.md) explains the difference between a one-file SDK helper and the example's folder script. For production application lifetime, read [async applications](guides/async-applications.md).
