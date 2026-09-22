"""Delete every document in the configured project and wait for deletion receipts."""

from __future__ import annotations

import argparse

from ragwell import AsyncRagwell, RagwellError
from ragwell.async_client import AsyncProject

from common import list_documents, load_settings, positive_seconds, report_error, run


async def clean_project(project: AsyncProject, timeout: int, *, yes: bool) -> int:
    # Snapshot every page before mutating the collection we just listed.
    documents = await list_documents(project)
    print(f"Project {project.id}: {len(documents)} document(s) to delete")
    for document in documents:
        print(f"  {document.original_filename!r} | {document.id} | {document.state}")
    if documents and not yes:
        print(
            "Rerun with --yes to delete ALL these project documents. Local files stay intact."
        )
        return 2

    cleaned = errors = 0
    for document in documents:
        try:
            receipt = await project.documents.delete(document.id)
            print(
                f"Delete {document.original_filename!r}: receipt={receipt.id}; waiting…",
                flush=True,
            )
            completed = await project.deletions.wait(receipt.id, timeout=timeout)
            cleaned += 1
            print(f"  {document.id}: {completed.state}")
        except RagwellError as error:
            errors += 1
            report_error(error)

    remaining = await list_documents(project)
    print(f"\nCleanup: cleaned={cleaned}, errors={errors}, remaining={len(remaining)}")
    for document in remaining:
        print(
            f"  Remaining: {document.original_filename!r} | {document.id} | {document.state}"
        )
    complete = not errors and not remaining
    print(
        "Project is clean."
        if complete
        else "Cleanup is incomplete; review the status above."
    )
    return 0 if complete else 1


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--yes",
        action="store_true",
        help="delete all documents in the configured project",
    )
    parser.add_argument(
        "--timeout",
        type=positive_seconds,
        default=300,
        help="seconds per deletion (default: 300)",
    )
    args = parser.parse_args()
    settings = load_settings()
    async with AsyncRagwell(
        base_url=settings.base_url, api_key=settings.api_key
    ) as client:
        return await clean_project(
            client.project(settings.project_id), args.timeout, yes=args.yes
        )


if __name__ == "__main__":
    run(main())
