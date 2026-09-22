"""Shared configuration and terminal output for the three scripts."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import Coroutine
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

from dotenv import load_dotenv
from ragwell import RagwellError
from ragwell.async_client import AsyncProject
from ragwell.types import DocumentResponse, DocumentState

EXAMPLE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str = field(repr=False)
    project_id: UUID
    sync_folder: Path


def load_settings() -> Settings:
    # Load only this example's .env. Explicit shell variables take precedence.
    load_dotenv(EXAMPLE_DIR / ".env", override=False)
    names = ("RAGWELL_BASE_URL", "RAGWELL_API_KEY", "RAGWELL_PROJECT_ID")
    values = {name: os.environ.get(name, "").strip() for name in names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ValueError("Set these variables in .env: " + ", ".join(missing))
    if urlsplit(values["RAGWELL_BASE_URL"]).path.strip("/"):
        raise ValueError("RAGWELL_BASE_URL must be the API origin, without /v1")
    try:
        project_id = UUID(values["RAGWELL_PROJECT_ID"])
    except ValueError:
        raise ValueError("RAGWELL_PROJECT_ID must be a project UUID") from None
    folder = Path(os.environ.get("SYNC_FOLDER", "documents")).expanduser()
    if not folder.is_absolute():
        folder = EXAMPLE_DIR / folder
    return Settings(
        values["RAGWELL_BASE_URL"], values["RAGWELL_API_KEY"], project_id, folder
    )


def positive_seconds(value: str) -> int:
    seconds = int(value)
    if seconds <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive number of seconds")
    return seconds


async def list_documents(project: AsyncProject) -> list[DocumentResponse]:
    # The SDK iterator visits every page. Deleted tombstones are not live documents.
    return [
        document
        async for document in project.documents.iter()
        if document.state != DocumentState.DELETED
    ]


async def show_status(project: AsyncProject) -> int:
    documents = await list_documents(project)
    print(f"\nProject {project.id}: {len(documents)} document(s)")
    not_searchable = 0
    for document in documents:
        inspection = await project.documents.inspect(document.id)
        job = inspection.latest_job
        processing = (
            f"{job.status} / {job.stage} / {job.progress_percent}%" if job else "no job"
        )
        print(
            f"  {document.original_filename!r} | {document.id} | {document.state}"
            f" | searchable={inspection.searchable} | {processing}"
        )
        not_searchable += not inspection.searchable
    return not_searchable


def report_error(error: RagwellError) -> None:
    print(f"{type(error).__name__}: {error}", file=sys.stderr)
    # These SDK identifiers help resume accepted work after a timeout/interruption.
    for name in ("document_id", "upload_id", "job_id", "receipt_id"):
        if name in error.identifiers:
            print(f"  {name}={error.identifiers[name]}", file=sys.stderr)


def run(command: Coroutine[None, None, int]) -> None:
    try:
        code = asyncio.run(command)
    except RagwellError as error:
        report_error(error)
        code = 1
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        code = 1
    except KeyboardInterrupt:
        print(
            "Stopped locally; accepted work may continue on the API.", file=sys.stderr
        )
        code = 130
    raise SystemExit(code)
