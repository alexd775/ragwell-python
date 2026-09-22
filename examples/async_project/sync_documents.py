"""Upload missing filenames and wait for their processing to finish."""

from __future__ import annotations

import argparse
from pathlib import Path

from ragwell import AsyncRagwell, RagwellError
from ragwell.async_client import AsyncProject

from common import (
    list_documents,
    load_settings,
    positive_seconds,
    report_error,
    run,
    show_status,
)

MEDIA_TYPES = {".pdf": "application/pdf", ".txt": "text/plain", ".md": "text/markdown"}
PENDING_JOBS = {"queued", "running", "retry_wait", "cancellation_requested"}


async def sync_documents(project: AsyncProject, folder: Path, timeout: int) -> int:
    if not folder.is_dir():
        raise ValueError(f"Sync folder does not exist: {folder}")
    documents = await list_documents(project)
    existing = {document.original_filename for document in documents}
    uploaded = skipped = errors = 0
    print(f"Project {project.id}: syncing {folder}")

    local_names: set[str] = set()
    # One level, sequential uploads: easy to follow and gentle on project quotas.
    for path in sorted(folder.iterdir()):
        if (
            path.is_symlink()
            or not path.is_file()
            or path.suffix.lower() not in MEDIA_TYPES
        ):
            print(f"Ignore {path.name!r}: use regular .pdf, .txt or .md files")
            continue
        local_names.add(path.name)
        if path.name in existing:
            print(f"Skip {path.name!r}: filename already in project")
            skipped += 1
            continue
        try:
            print(f"Upload {path.name!r}", flush=True)
            intake = await project.documents.upload(
                file=path, media_type=MEDIA_TYPES[path.suffix.lower()]
            )
            existing.add(path.name)
            uploaded += 1
            print(
                f"  Accepted document={intake.document.id}, job={intake.job_id}",
                flush=True,
            )
            completed_job = await project.jobs.wait(intake.job_id, timeout=timeout)
            print(f"  Processing: {completed_job.status}")
        except RagwellError as error:
            errors += 1
            report_error(error)

    # Reruns observe existing pending jobs instead of uploading the files again.
    for document in documents:
        if document.original_filename not in local_names:
            continue
        try:
            inspection = await project.documents.inspect(document.id)
            job = inspection.latest_job
            if job is not None and job.status in PENDING_JOBS:
                print(
                    f"Wait for {document.original_filename!r}: job={job.id}", flush=True
                )
                await project.jobs.wait(job.id, timeout=timeout)
        except RagwellError as error:
            errors += 1
            report_error(error)

    pending = await show_status(project)
    print(
        f"\nSync: uploaded={uploaded}, skipped={skipped}, errors={errors}, not_searchable={pending}"
    )
    return 1 if errors or pending else 0


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=positive_seconds,
        default=300,
        help="seconds per job (default: 300)",
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="list documents and processing status without uploading or waiting",
    )
    args = parser.parse_args()
    settings = load_settings()
    async with AsyncRagwell(
        base_url=settings.base_url, api_key=settings.api_key
    ) as client:
        project = client.project(settings.project_id)
        if args.status_only:
            await show_status(project)
            return 0
        return await sync_documents(project, settings.sync_folder, args.timeout)


if __name__ == "__main__":
    run(main())
