"""Opt-in installed-wheel lifecycle validation against an existing beta endpoint."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import inspect
import json
import math
import os
import stat
import sys
import tempfile
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import httpx

from qualification.evidence import installed_identity, service_projection
from ragwell import ApiError, AsyncRagwell, NotFoundError, Ragwell, RagwellError
from ragwell.async_client import AsyncProject
from ragwell.client import Project
from ragwell.types import CreateDocumentExportRequest, SearchFilters

REQUIRED_SCOPES = (
    "project:read",
    "document:upload",
    "document:read",
    "job:read",
    "retrieval:search",
    "document:delete",
    "deletion:read",
)
MAX_OPENAPI_BYTES = 4 * 1024 * 1024
MAX_EXPORT_BYTES = 1024 * 1024
MAX_EXPORT_PARTS = 10
T = TypeVar("T")


class CheckFailed(Exception):
    """A fixed, content-free validation check name."""


def require(condition: object, check: str) -> None:
    if not condition:
        raise CheckFailed(check)


def endpoint(value: str) -> str:
    url = urlsplit(value)
    require(
        all(ord(char) > 32 for char in value)
        and url.scheme == "https"
        and url.hostname
        and url.username is None
        and url.password is None
        and not url.query
        and not url.fragment
        and url.path in ("", "/"),
        "https_api_origin_required",
    )
    _ = url.port  # Reject malformed ports before any network or report metadata.
    return value.rstrip("/")


def read_key(path: Path) -> str:
    # Open the same regular file we inspect; reject symlinks on POSIX.
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as source:
        info = os.fstat(source.fileno())
        require(stat.S_ISREG(info.st_mode), "credential_file_required")
        require(
            os.name != "posix" or not info.st_mode & 0o077,
            "credential_file_permissions",
        )
        raw = source.read(4097)
    require(0 < len(raw) <= 4096, "credential_file_size")
    key = raw.decode("ascii").strip()
    require(
        key and all(33 <= ord(char) <= 126 for char in key), "credential_file_format"
    )
    return key


def failure(exc: BaseException) -> dict[str, object]:
    # Never serialize exception text, response bodies or arbitrary server strings.
    detail: dict[str, object] = {"error_type": type(exc).__name__}
    if isinstance(exc, CheckFailed):
        detail["check"] = str(exc)
    if isinstance(exc, ApiError):
        detail["http_status"] = exc.status_code
        try:
            detail["request_id"] = str(UUID(exc.request_id or ""))
        except ValueError:
            pass
    return detail


class Report:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, Any] = {
            "report_version": 1,
            "qualification": "beta_lifecycle",
            "status": "running",
            "run_id": str(uuid4()),
            "started_at": datetime.now(UTC).isoformat(),
            "required_scopes": list(REQUIRED_SCOPES),
            "styles": {style: {"status": "not_run"} for style in ("sync", "async")},
        }
        # Reject an existing report before any credentials or network are used.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
        self.save()

    def save(self) -> None:
        temporary: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", dir=self.path.parent, delete=False
            ) as out:
                temporary = out.name
                json.dump(self.data, out, indent=2, sort_keys=True)
                out.write("\n")
                out.flush()
                os.fsync(out.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)


def live_contract(base_url: str, contract: dict[str, Any]) -> str:
    started = time.monotonic()
    body = bytearray()
    with httpx.Client(trust_env=False, follow_redirects=False, timeout=30) as client:
        with client.stream("GET", base_url + "/openapi.json") as response:
            response.raise_for_status()
            for chunk in response.iter_bytes():
                require(time.monotonic() - started < 30, "openapi_deadline")
                require(len(body) + len(chunk) <= MAX_OPENAPI_BYTES, "openapi_size")
                body.extend(chunk)
    return hashlib.sha256(
        service_projection(json.loads(body), contract["x-ragwell-artifact-version"])
    ).hexdigest()


async def resolve(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await value
    return value


async def cleanup(
    project: Project | AsyncProject,
    record: dict[str, Any],
    save: Callable[[], None],
    wait_timeout: float,
) -> None:
    if "upload_id" in record and "document_id" not in record:
        upload = await resolve(project.uploads.get(record["upload_id"]))
        if upload.state.value == "finalized" and upload.document_id is not None:
            record["document_id"] = str(upload.document_id)
            save()
        else:
            record["cleanup"] = {
                "status": "upload_requires_expiry",
                "upload_id": record["upload_id"],
            }
            return
    if "document_id" not in record:
        record["cleanup"] = {
            "status": "acceptance_unknown"
            if record.get("upload_started")
            else "not_needed"
        }
        return
    receipt = await resolve(
        project.documents.delete(
            record["document_id"], idempotency_key=record["delete_key"]
        )
    )
    require(receipt.document_id == UUID(record["document_id"]), "deletion_identity")
    record["receipt_id"] = str(receipt.id)
    save()
    completed = await resolve(
        project.deletions.wait(receipt.id, timeout=wait_timeout, initial_interval=2)
    )
    require(
        completed.id == receipt.id and completed.document_id == receipt.document_id,
        "deletion_identity",
    )
    try:
        await resolve(project.documents.get(record["document_id"]))
    except NotFoundError:
        pass
    else:
        raise CheckFailed("deleted_document_still_readable")
    record["cleanup"] = {"status": "deleted", "receipt_id": str(receipt.id)}


async def run_style(
    client: Ragwell | AsyncRagwell,
    project_id: UUID,
    style: str,
    report: Report,
    wait_timeout: float,
) -> bool:
    project = client.project(project_id)
    record: dict[str, Any] = {
        "status": "running",
        "phase": "project",
        "delete_key": uuid4().hex,
    }
    report.data["styles"][style] = record
    report.save()
    marker = "Ragwell synthetic validation " + report.data["run_id"] + " " + style
    content = (
        marker + ".\nThe fictional observatory stores purple lanterns in room seven.\n"
    ).encode()
    record["fixture_sha256"] = hashlib.sha256(content).hexdigest()
    record["fixture_bytes"] = len(content)
    interrupted: BaseException | None = None
    try:
        require((await resolve(project.get())).id == project_id, "project_identity")
        record["phase"] = "upload"
        record["upload_started"] = True
        record["upload_key"] = uuid4().hex
        report.save()
        try:
            intake = await resolve(
                project.documents.upload(
                    file=content,
                    filename=f"sdk-validation-{report.data['run_id']}-{style}.txt",
                    media_type="text/plain",
                    idempotency_key=record["upload_key"],
                )
            )
        except RagwellError as exc:
            # Recover only this upload's identifiers, never enumerate project data.
            for name in ("upload_id", "document_id", "job_id"):
                value = exc.identifiers.get(name)
                if value:
                    record[name] = str(UUID(value))
            report.save()
            raise
        record.update(
            upload_id=str(intake.upload.id),
            document_id=str(intake.document.id),
            job_id=str(intake.job_id),
        )
        record["phase"] = "processing"
        report.save()
        job = await resolve(
            project.jobs.wait(intake.job_id, timeout=wait_timeout, initial_interval=2)
        )
        doc = intake.document.id
        require(
            job.document_id == doc and job.document_version_id == intake.version.id,
            "job_identity",
        )
        inspection = await resolve(project.documents.inspect(doc))
        generation = inspection.active_generation_id
        if generation is None:
            raise CheckFailed("searchable_generation")
        require(
            inspection.document_id == doc and inspection.searchable,
            "searchable_generation",
        )
        record["generation_id"] = str(generation)
        record["phase"] = "search"
        report.save()
        results = await resolve(
            project.search(query=marker, filters=SearchFilters(document_ids=[doc]), k=3)
        )
        require(results.items, "retrieval_empty")
        require(
            all(
                hit.document_id == doc and hit.document_version_id == intake.version.id
                for hit in results.items
            ),
            "retrieval_identity",
        )
        require(
            any(marker in hit.content for hit in results.items),
            "retrieval_authored_content",
        )
        require(
            all(
                hit.citation is not None
                and hit.parts
                and math.isfinite(hit.scores.final)
                for hit in results.items
            ),
            "retrieval_provenance",
        )
        record["retrieval_id"] = str(results.retrieval_id)
        record["phase"] = "export"
        report.save()
        export = await resolve(
            project.documents.exports.create(
                doc,
                CreateDocumentExportRequest(
                    generation_id=generation, include_embeddings=False
                ),
            )
        )
        record["export_id"] = str(export.id)
        report.save()
        export = await resolve(
            project.documents.exports.wait(
                doc, export.id, timeout=wait_timeout, initial_interval=2
            )
        )
        require(
            export.generation_id == generation
            and export.document_version_id == intake.version.id
            and not export.include_embeddings,
            "export_identity",
        )
        require(
            0 < len(export.parts) == export.total_parts <= MAX_EXPORT_PARTS,
            "export_parts",
        )
        require(
            len({part.part_number for part in export.parts}) == len(export.parts),
            "export_duplicate_parts",
        )
        require(
            all(0 < part.byte_size <= MAX_EXPORT_BYTES for part in export.parts)
            and sum(part.byte_size for part in export.parts)
            == export.total_bytes
            <= MAX_EXPORT_BYTES,
            "export_size",
        )
        with tempfile.TemporaryDirectory(prefix="ragwell-beta-export-") as directory:
            for part in export.parts:
                await resolve(
                    project.documents.exports.download_part(
                        doc,
                        export.id,
                        part,
                        Path(directory) / f"{part.part_number}.ndjson",
                    )
                )
        record["export_parts"] = export.total_parts
        record["export_bytes"] = export.total_bytes
        record["checks"] = [
            "project",
            "upload",
            "processing",
            "inspection",
            "retrieval_content_and_provenance",
            "verified_export",
        ]
    except BaseException as exc:
        record["error"] = failure(exc)
        if not isinstance(exc, Exception):
            interrupted = exc
    finally:
        record["failed_phase"] = record["phase"] if "error" in record else None
        record["phase"] = "cleanup"

        def cleanup_checkpoint() -> None:
            try:
                report.save()
            except OSError as exc:
                # A full/read-only report disk must not prevent remote cleanup.
                record["report_error"] = failure(exc)

        cleanup_checkpoint()
        try:
            await cleanup(project, record, cleanup_checkpoint, wait_timeout)
        except BaseException as exc:
            record["cleanup"] = {"status": "failed", **failure(exc)}
            if not isinstance(exc, Exception):
                interrupted = exc
        record["status"] = (
            "passed"
            if "error" not in record
            and "report_error" not in record
            and record["cleanup"]["status"] == "deleted"
            else "failed"
        )
        report.save()
    if interrupted is not None:
        raise interrupted
    return bool(record["status"] == "passed")


async def execute(args: argparse.Namespace, report: Report) -> int:
    try:
        base_url = endpoint(args.base_url)
        project_id = UUID(args.project_id)
        require(
            math.isfinite(args.wait_timeout) and 1 <= args.wait_timeout <= 600,
            "wait_timeout_range",
        )
        identity, contract = installed_identity(args.wheel)
        report.data.update(
            identity,
            base_url=base_url,
            project_id=str(project_id),
            wait_timeout_seconds=args.wait_timeout,
            runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            evidence_module_sha256=hashlib.sha256(
                Path(__file__).with_name("evidence.py").read_bytes()
            ).hexdigest(),
        )
        observed = live_contract(base_url, contract)
        report.data["runtime_contract_sha256"] = observed
        report.save()
        require(observed == identity["machine_sha256"], "running_contract_mismatch")
        key = read_key(Path(os.environ["RAGWELL_BETA_API_KEY_FILE"]))
        with Ragwell(
            base_url=base_url, api_key=key, operation_timeout=30, transfer_timeout=60
        ) as client:
            passed = await run_style(
                client, project_id, "sync", report, args.wait_timeout
            )
        if passed:
            async with AsyncRagwell(
                base_url=base_url,
                api_key=key,
                operation_timeout=30,
                transfer_timeout=60,
            ) as async_client:
                passed = await run_style(
                    async_client, project_id, "async", report, args.wait_timeout
                )
        report.data["status"] = "passed" if passed else "failed"
        return 0 if passed else 1
    except BaseException as exc:
        report.data.update(status="failed", error=failure(exc))
        return (
            130 if isinstance(exc, (KeyboardInterrupt, asyncio.CancelledError)) else 1
        )
    finally:
        report.data["finished_at"] = datetime.now(UTC).isoformat()
        report.save()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wait-timeout", type=float, default=180)
    args = parser.parse_args()
    try:
        report = Report(args.output)
        code = asyncio.run(execute(args, report))
    except (Exception, KeyboardInterrupt) as exc:
        print(
            f"Beta validation could not finish ({type(exc).__name__}).", file=sys.stderr
        )
        raise SystemExit(1) from None
    print(f"Beta lifecycle validation: {report.data['status']}.")
    raise SystemExit(code)


if __name__ == "__main__":
    main()
