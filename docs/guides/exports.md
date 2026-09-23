# Export a document generation

An export is an asynchronous operation. Create it, wait for the export state to succeed, then download its manifest parts. The SDK's `download_part()` checks byte size and SHA-256 before installing each file.

```python
from pathlib import Path

from ragwell.types import CreateDocumentExportRequest

export = await project.documents.exports.create(
    document_id,
    CreateDocumentExportRequest(
        generation_id=generation_id,
        include_embeddings=False,
    ),
)
export = await project.documents.exports.wait(document_id, export.id, timeout=300)
for part in export.parts:
    saved = await project.documents.exports.download_part(
        document_id,
        export.id,
        part,
        Path(f"part-{part.part_number}.ndjson"),
    )
    print(saved.path)
```

Downloads refuse to overwrite an existing destination unless you pass `overwrite=True`. They use a temporary file in the destination directory and replace atomically after verification. `stream_part()` gives you a context-managed byte stream when your application wants to handle the bytes itself; the stream alone does not verify the manifest.

A wait timeout does not cancel the export. Keep the `export.id` and call `exports.get()` or `exports.wait()` later. Export parts can expire; inspect the export result before downloading. See the [client reference](../reference/client-and-resources.md) and [reliability details](../reliability.md).
