"""Installed-wheel HTTP qualification against authorized synthetic fixtures."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import tempfile
from importlib.metadata import distribution
from pathlib import Path
from typing import Any

import ragwell
from ragwell import AsyncRagwell, NotFoundError, PermissionDeniedError, Ragwell
from ragwell.types import CreateDocumentExportRequest, SearchFilters

MACHINE_SHA256 = "06d0efac740946c21f0ddfa3d873e2197cf4924487ed512d08b8c2fd824978bd"


def _assert_installed_wheel() -> None:
    repository = Path(__file__).resolve().parents[1]
    package = Path(ragwell.__file__).resolve()
    if package.is_relative_to(repository):
        raise SystemExit(
            "Qualification must run from an installed wheel outside the source checkout"
        )


def _foreign_project_is_hidden(client: Ragwell, foreign_project_id: str) -> None:
    try:
        client.project(foreign_project_id).get()
    except (PermissionDeniedError, NotFoundError):
        return
    raise AssertionError("Foreign project was not denied")


def _sync_lifecycle(
    *, base_url: str, api_key: str, project_id: str, fixture: Path
) -> dict[str, Any]:
    with Ragwell(base_url=base_url, api_key=api_key) as client:
        project = client.project(project_id)
        project.get()
        client.upload_policy.get()
        completion = project.documents.upload_and_wait(file=fixture, wait_timeout=300)
        document_id = completion.intake.document.id
        search = project.search(
            query="qualification marker",
            filters=SearchFilters(document_ids=[document_id]),
        )
        inspection = project.documents.inspect(document_id)
        generations = list(project.documents.generations.iter(document_id))
        if not generations:
            raise AssertionError("Successful ingestion exposed no generation")
        export = project.documents.exports.create(
            document_id,
            CreateDocumentExportRequest(generation_id=generations[0].id),
        )
        manifest = project.documents.exports.wait(document_id, export.id)
        with tempfile.TemporaryDirectory(prefix="ragwell-http-qualification-") as temp:
            directory = Path(temp)
            for part in manifest.parts:
                project.documents.exports.download_part(
                    document_id,
                    manifest.id,
                    part,
                    directory / f"part-{part.part_number}.ndjson",
                )
        receipt = project.documents.delete(document_id)
        project.deletions.wait(receipt.id)
        return {
            "document_id": str(document_id),
            "job_id": str(completion.job.id),
            "retrieval_id": str(search.retrieval_id),
            "inspection_generation_id": (
                str(inspection.active_generation_id)
                if inspection.active_generation_id is not None
                else None
            ),
            "export_id": str(manifest.id),
            "deletion_receipt_id": str(receipt.id),
        }


async def _async_lifecycle(
    *, base_url: str, api_key: str, project_id: str, fixture: Path
) -> dict[str, str]:
    async with AsyncRagwell(base_url=base_url, api_key=api_key) as client:
        project = client.project(project_id)
        await project.get()
        completion = await project.documents.upload_and_wait(
            file=fixture, wait_timeout=300
        )
        result = await project.search(
            query="qualification marker",
            filters=SearchFilters(document_ids=[completion.intake.document.id]),
        )
        receipt = await project.documents.delete(completion.intake.document.id)
        await project.deletions.wait(receipt.id)
        return {
            "document_id": str(completion.intake.document.id),
            "job_id": str(completion.job.id),
            "retrieval_id": str(result.retrieval_id),
            "deletion_receipt_id": str(receipt.id),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--foreign-project-id", required=True)
    parser.add_argument("--sync-fixture", type=Path, required=True)
    parser.add_argument("--async-fixture", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    _assert_installed_wheel()
    with Ragwell(base_url=arguments.base_url, api_key=arguments.api_key) as client:
        _foreign_project_is_hidden(client, arguments.foreign_project_id)
    sync_result = _sync_lifecycle(
        base_url=arguments.base_url,
        api_key=arguments.api_key,
        project_id=arguments.project_id,
        fixture=arguments.sync_fixture,
    )
    async_result = asyncio.run(
        _async_lifecycle(
            base_url=arguments.base_url,
            api_key=arguments.api_key,
            project_id=arguments.project_id,
            fixture=arguments.async_fixture,
        )
    )
    wheel_distribution = distribution("ragwell")
    report = {
        "artifact_machine_sha256": MACHINE_SHA256,
        "sdk_version": wheel_distribution.version,
        "wheel_sha256": hashlib.sha256(arguments.wheel.read_bytes()).hexdigest(),
        "sync": sync_result,
        "async": async_result,
        "limitations": [
            "Controlled retry/cancel, expired-export, and failed-deletion fixtures must be supplied by the service owner in a separate authorized run."
        ],
    }
    arguments.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
