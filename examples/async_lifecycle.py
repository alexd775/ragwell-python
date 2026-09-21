"""Framework-neutral async lifecycle; reuse the client in your application."""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4

from ragwell import AsyncRagwell
from ragwell.types import CreateDocumentExportRequest, SearchFilters


async def lifecycle(client: AsyncRagwell, project_id: str) -> dict[str, str | int]:
    project = client.project(project_id)
    intake = await project.documents.upload(
        file=b"The fictional observatory stores purple lanterns in room seven.\n",
        filename=f"sdk-example-{uuid4().hex}.txt",
    )
    document_id = intake.document.id
    try:
        await project.jobs.wait(intake.job_id, timeout=300)
        result = await project.search(
            query="Where are the purple lanterns stored?",
            filters=SearchFilters(document_ids=[document_id]),
        )
        inspection = await project.documents.inspect(document_id)
        generation = inspection.active_generation_id
        if generation is None:
            raise RuntimeError("Processing completed without a searchable generation")
        export = await project.documents.exports.create(
            document_id,
            CreateDocumentExportRequest(
                generation_id=generation, include_embeddings=False
            ),
        )
        export = await project.documents.exports.wait(
            document_id, export.id, timeout=300
        )
        with tempfile.TemporaryDirectory(prefix="ragwell-example-") as directory:
            for part in export.parts:
                await project.documents.exports.download_part(
                    document_id,
                    export.id,
                    part,
                    Path(directory) / f"part-{part.part_number}.ndjson",
                )
        summary: dict[str, str | int] = {
            "document_id": str(document_id),
            "retrieval_id": str(result.retrieval_id),
            "result_count": len(result.items),
            "export_parts": export.total_parts,
        }
    finally:
        receipt = await project.documents.delete(document_id)
        await project.deletions.wait(receipt.id, timeout=300)
    return {**summary, "deletion_receipt_id": str(receipt.id)}


async def main() -> None:
    # Applications normally own this context for their complete lifespan.
    async with AsyncRagwell() as client:
        print(json.dumps(await lifecycle(client, os.environ["RAGWELL_PROJECT_ID"])))


if __name__ == "__main__":
    asyncio.run(main())
