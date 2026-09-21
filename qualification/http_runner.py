"""Qualify an installed wheel over real HTTP using API-owner synthetic fixtures."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import inspect
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import httpx
from evidence import (
    AsyncFaultTransport,
    Evidence,
    FaultTransport,
    installed_identity,
    service_projection,
)

from ragwell import (
    ApiError,
    AsyncRagwell,
    OperationFailedError,
    Ragwell,
    WaitTimeoutError,
)
from ragwell.types import (
    CreateDocumentExportRequest,
    CreateUploadRequest,
    CreateUploadRequestDeclaredMediaType,
    DocumentMetadataInput,
    IngestionJobStatus,
    ReplaceDocumentMetadataRequest,
    SearchFilters,
)


async def resolve(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


async def close(client: Any) -> None:
    if isinstance(client, AsyncRagwell):
        await client.aclose()
    else:
        client.close()


async def collect(value: Any) -> list[Any]:
    if hasattr(value, "__aiter__"):
        return [item async for item in value]
    return list(value)


async def denied(call: Any, statuses: set[int] | None = None) -> str:
    try:
        await resolve(call())
    except ApiError as exc:
        assert exc.status_code in (statuses or {403, 404}), (
            f"Unexpected denial status {exc.status_code}"
        )
        return exc.code
    raise AssertionError("Operation unexpectedly allowed")


def creation(content: bytes, filename: str = "probe.txt") -> CreateUploadRequest:
    media = {".pdf": "application/pdf", ".txt": "text/plain", ".md": "text/markdown"}[
        Path(filename).suffix
    ]
    return CreateUploadRequest(
        original_filename=filename,
        declared_media_type=CreateUploadRequestDeclaredMediaType(media),
        declared_size_bytes=len(content),
        declared_sha256=hashlib.sha256(content).hexdigest(),
    )


async def matrix(client: Any, fixture: dict[str, Any]) -> list[Any]:
    p = client.project(fixture["project_id"])
    d, g, j, u, r, e, s = (
        fixture[key]
        for key in (
            "document_id",
            "generation_id",
            "job_id",
            "upload_id",
            "receipt_id",
            "export_id",
            "source_id",
        )
    )

    async def stream() -> None:
        result = await resolve(p.documents.exports.stream_part(d, e, 0))
        if hasattr(result, "__aenter__"):
            async with result:
                await collect(result.iter_bytes())
        else:
            with result:
                list(result.iter_bytes())

    return [
        lambda: p.get(),
        lambda: p.embedding_connection.get(),
        lambda: p.documents.list(),
        lambda: p.documents.get(d),
        lambda: p.documents.inspect(d),
        lambda: p.documents.activity(d),
        lambda: p.documents.generations.list(d),
        lambda: p.documents.chunks.list(d, g),
        lambda: p.documents.sources.get(d, g, s),
        lambda: p.documents.replace_metadata(
            d,
            ReplaceDocumentMetadataRequest(
                expected_revision=1, tags=[], metadata=DocumentMetadataInput()
            ),
        ),
        lambda: p.documents.delete(d),
        lambda: p.documents.exports.create(
            d, CreateDocumentExportRequest(generation_id=UUID(g))
        ),
        lambda: p.documents.exports.get(d, e),
        stream,
        lambda: p.jobs.list(),
        lambda: p.jobs.get(j),
        lambda: p.jobs.retry(j),
        lambda: p.jobs.cancel(j),
        lambda: p.deletions.get(r),
        lambda: p.deletions.retry(r),
        lambda: p.uploads.create(creation(b"probe")),
        lambda: p.uploads.get(u),
        lambda: p.uploads.upload_content(
            u, content=b"probe", content_type="text/plain"
        ),
        lambda: p.uploads.finalize(u),
        lambda: p.search(query="qualification marker"),
    ]


async def run_style(
    style: str,
    manifest: dict[str, Any],
    credentials: dict[str, str],
    contract: dict[str, Any],
    report: dict[str, Any],
) -> None:
    evidence = Evidence(contract)
    cls = Ragwell if style == "sync" else AsyncRagwell

    def client(key: str) -> Any:
        transport = (
            FaultTransport(evidence)
            if style == "sync"
            else AsyncFaultTransport(evidence)
        )
        return cls(
            base_url=manifest["base_url"], api_key=credentials[key], transport=transport
        )

    root = client("owner")
    owner, foreign = manifest["tenants"]["owner"], manifest["tenants"]["foreign"]
    project = root.project(owner["project_id"])
    base = f"/v1/projects/{owner['project_id']}"
    created: list[str] = []
    cleanup: list[dict[str, str]] = []
    intakes: list[dict[str, Any]] = []
    report.update(status="running", checks=[], cleanup=cleanup, intakes=intakes)

    def check(name: str) -> None:
        report["checks"].append(name)
        print(f"{style}: {name}", flush=True)

    def drop(method: str, path: str) -> None:
        evidence.drop = method, base + path

    try:
        report["step"] = "authorization"
        evidence.phase = "foreign_project"
        for call in await matrix(root, foreign):
            await denied(call)
        # Owner project plus foreign nested identifiers (list/search have no object path).
        evidence.phase = "foreign_objects"
        calls = await matrix(root, {**foreign, "project_id": owner["project_id"]})
        for index in (
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            15,
            16,
            17,
            18,
            19,
            21,
            22,
            23,
        ):
            await denied(calls[index])
        # Independently reject a foreign generation, source and export below an owned document.
        for field, indexes in (
            ("generation_id", (7, 8, 11)),
            ("source_id", (8,)),
            ("export_id", (12, 13)),
        ):
            calls = await matrix(root, {**owner, field: foreign[field]})
            for index in indexes:
                await denied(calls[index])
        evidence.phase = "missing_scope"
        scoped = client("read_only")
        try:
            calls = await matrix(scoped, owner)
            for index, call in enumerate(calls):
                if index not in (0, 1):
                    await denied(call, {403})
        finally:
            await close(scoped)
        scoped = client("search_only")
        try:
            calls = await matrix(scoped, owner)
            for index in (0, 1):
                await denied(calls[index], {403})
        finally:
            await close(scoped)
        evidence.phase = "revoked"
        revoked = client("revoked")
        try:
            await denied(lambda: revoked.project(owner["project_id"]).get(), {401})
        finally:
            await close(revoked)
        evidence.phase = "positive"
        check(
            "two-tenant objects, nested ownership, every operation scope, revoked key"
        )
        report["step"] = "intake"
        assert (await resolve(root.upload_policy.get())).formats
        assert str((await resolve(project.get())).id) == owner["project_id"]
        await resolve(project.embedding_connection.get())
        for item in manifest["fixtures"]:
            file = Path(item["path"])
            content = file.read_bytes()
            assert hashlib.sha256(content).hexdigest() == item["sha256"]
            request = creation(content, file.name)
            key = uuid4().hex
            drop("POST", "/uploads")
            upload = await resolve(project.uploads.create(request, idempotency_key=key))
            record: dict[str, Any] = {
                "upload_id": str(upload.id),
                "fixture_sha256": item["sha256"],
                "format": file.suffix,
            }
            intakes.append(record)
            replay = await resolve(project.uploads.create(request, idempotency_key=key))
            assert upload.id == replay.id
            drop("PUT", f"/uploads/{upload.id}/content")
            await resolve(
                project.uploads.upload_content(
                    upload.id,
                    content=content,
                    content_type=request.declared_media_type.value,
                )
            )
            drop("POST", f"/uploads/{upload.id}/finalize")
            intake = await resolve(project.uploads.finalize(upload.id))
            d = str(intake.document.id)
            created.append(d)
            record.update(document_id=d, job_id=str(intake.job_id))
            recovered = await resolve(project.uploads.get(upload.id))
            assert (
                recovered.document_id == intake.document.id
                and recovered.job_id == intake.job_id
            )
            await resolve(
                project.jobs.wait(intake.job_id, timeout=120, initial_interval=0.05)
            )
            document = await resolve(project.documents.get(d))
            body = ReplaceDocumentMetadataRequest(
                expected_revision=document.metadata_revision,
                tags=[style, "qualification"],
                metadata=DocumentMetadataInput(
                    source="fixture", author="sdk", language="en", category="reference"
                ),
            )
            key = uuid4().hex
            drop("PUT", f"/documents/{d}/metadata")
            updated = await resolve(
                project.documents.replace_metadata(d, body, idempotency_key=key)
            )
            replay = await resolve(
                project.documents.replace_metadata(d, body, idempotency_key=key)
            )
            assert replay.command.replayed and updated.command.id == replay.command.id
            assert replay.command.applied_revision == document.metadata_revision + 1
            stale = ReplaceDocumentMetadataRequest(
                expected_revision=document.metadata_revision,
                tags=["conflicting"],
                metadata=body.metadata,
            )
            await denied(
                lambda d=d, stale=stale: project.documents.replace_metadata(d, stale),
                {409},
            )
            # Replay remains tied to the original acceptance after a later revision.
            newer = ReplaceDocumentMetadataRequest(
                expected_revision=replay.metadata_revision,
                tags=[style, "qualification", "revised"],
                metadata=body.metadata,
            )
            current = await resolve(project.documents.replace_metadata(d, newer))
            old = await resolve(
                project.documents.replace_metadata(d, body, idempotency_key=key)
            )
            assert old.metadata_revision == current.metadata_revision
            assert old.command.applied_revision == document.metadata_revision + 1
            report["step"] = "retrieval/provenance"
            result = await resolve(
                project.search(
                    query=manifest["marker"],
                    filters=SearchFilters(
                        document_ids=[UUID(d)],
                        tags_all=[style],
                        source_any=["fixture"],
                        author_any=["sdk"],
                        language_any=["en"],
                        category_any=["reference"],
                    ),
                )
            )
            assert result.items and result.retrieval_version and result.profile_id
            generations = await collect(project.documents.generations.iter(d, limit=1))
            assert len(generations) == 1
            g = generations[0].id
            inspection = await resolve(project.documents.inspect(d))
            assert inspection.active_generation_id == g
            await resolve(project.documents.activity(d))
            chunks = await collect(
                project.documents.chunks.iter(d, g, limit=10, text=manifest["marker"])
            )
            assert chunks
            record.update(
                generation_id=str(g),
                chunk_count=len(chunks),
                retrieval_id=str(result.retrieval_id),
                retrieval_version=result.retrieval_version,
                profile_id=result.profile_id,
            )
            by_id = {c.id: c for c in chunks}
            for hit in result.items:
                assert (
                    str(hit.document_id) == d
                    and hit.document_version_id == intake.version.id
                )
                assert hit.chunk_id in by_id and manifest["marker"] in hit.content
                assert hit.parts and hit.citation and hit.representation_version
                assert math.isfinite(hit.scores.final)
                assert all(
                    math.isfinite(v)
                    for v in hit.scores.to_dict().values()
                    if isinstance(v, (int, float))
                )
                for part in hit.parts:
                    if part.source_id and part.span:
                        span = part.span.to_dict()
                        source = await resolve(
                            project.documents.sources.get(
                                d,
                                g,
                                part.source_id,
                                offset=span["start_offset"],
                                limit=span["end_offset"] - span["start_offset"],
                            )
                        )
                        assert part.text == source.content
            report["step"] = "exports"
            for embeddings in (False, True) if file.suffix == ".txt" else ():
                assert len(chunks) > 100
                body = CreateDocumentExportRequest(
                    generation_id=g, include_embeddings=embeddings
                )
                key = uuid4().hex
                drop("POST", f"/documents/{d}/exports")
                export = await resolve(
                    project.documents.exports.create(d, body, idempotency_key=key)
                )
                replay = await resolve(
                    project.documents.exports.create(d, body, idempotency_key=key)
                )
                assert export.id == replay.id and replay.command.replayed
                export = await resolve(
                    project.documents.exports.wait(
                        d, export.id, timeout=120, initial_interval=0.05
                    )
                )
                assert export.parts and export.include_embeddings == embeddings
                assert export.total_parts > 1
                record.setdefault("exports", []).append(
                    {
                        "id": str(export.id),
                        "part_count": export.total_parts,
                        "chunk_count": export.chunk_count,
                        "include_embeddings": embeddings,
                    }
                )
                rows = []
                with tempfile.TemporaryDirectory(
                    prefix="ragwell-verified-export-"
                ) as temp:
                    for part in export.parts:
                        destination = Path(temp) / f"{part.part_number}.ndjson"
                        await resolve(
                            project.documents.exports.download_part(
                                d, export.id, part, destination
                            )
                        )
                        data = destination.read_bytes()
                        assert (
                            len(data) == part.byte_size
                            and hashlib.sha256(data).hexdigest() == part.sha256
                        )
                        rows.extend(json.loads(line) for line in data.splitlines())
                headers = [row for row in rows if row["type"] == "manifest"]
                assert len(headers) == export.total_parts
                rows = [row for row in rows if row["type"] == "chunk"]
                assert len(rows) == export.chunk_count
                assert all(bool(row.get("embedding")) == embeddings for row in rows)
        check(
            "PDF/text/Markdown, intake recovery, revision conflict and replay, retrieval citations, exports with and without vectors"
        )
        report["step"] = "filters/pagination"
        filters = dict(
            document_ids=created,
            tags_all=[style],
            tags_any=["qualification"],
            source_any=["fixture"],
            author_any=["sdk"],
            language_any=["en"],
            category_any=["reference"],
        )
        documents = await collect(project.documents.iter(limit=1, **filters))
        assert {str(d.id) for d in documents} == set(created) and len(documents) == 3
        jobs = await collect(
            project.jobs.iter(limit=1, status=[IngestionJobStatus.SUCCEEDED], **filters)
        )
        assert {str(j.document_id) for j in jobs} == set(created) and len(jobs) == 3
        assert not (
            await resolve(project.documents.list(tags_all=["never-present"]))
        ).items
        assert not (
            await resolve(
                project.search(
                    query=manifest["marker"],
                    filters=SearchFilters(document_ids=[UUID(foreign["document_id"])]),
                )
            )
        ).items
        # These fields are deliberately absent from SDK types; probe the public wire directly.
        raw = (httpx.Client if style == "sync" else httpx.AsyncClient)(
            base_url=manifest["base_url"],
            trust_env=False,
            timeout=30,
            headers={"Authorization": f"Bearer {credentials['owner']}"},
        )
        try:
            for field in ("tenant_id", "organization_id", "project_id"):
                response = await resolve(
                    raw.post(
                        base + "/search",
                        json={
                            "query": "qualification",
                            "filters": {field: foreign["project_id"]},
                        },
                    )
                )
                assert response.status_code == 422
        finally:
            if style == "sync":
                raw.close()
            else:
                await raw.aclose()
        assert not (
            await resolve(project.documents.list(document_ids=[foreign["document_id"]]))
        ).items
        assert not (
            await resolve(project.jobs.list(document_ids=[foreign["document_id"]]))
        ).items
        for field in (
            "tags_all",
            "tags_any",
            "source_any",
            "author_any",
            "language_any",
            "category_any",
        ):
            empty = {field: ["not-present"]}
            assert not (await resolve(project.documents.list(**empty))).items
            assert not (await resolve(project.jobs.list(**empty))).items
            assert not (
                await resolve(
                    project.search(
                        query=manifest["marker"], filters=SearchFilters(**empty)
                    )
                )
            ).items
        page = await resolve(project.jobs.list(limit=1, **filters))
        assert page.next_cursor
        assert (
            await denied(
                lambda: project.jobs.list(
                    after=page.next_cursor, tags_all=["changed-filter"]
                ),
                {422},
            )
            == "invalid_cursor"
        )
        check("filtered document/job keyset pages and reserved authorization filters")
        report["step"] = "controlled lifecycle states"
        controls = owner[style]
        j = controls["cancel"]["job_id"]
        try:
            await resolve(project.jobs.wait(j, timeout=0))
        except WaitTimeoutError:
            pass
        else:
            raise AssertionError("Queued job unexpectedly completed")
        assert (await resolve(project.jobs.get(j))).status == IngestionJobStatus.QUEUED
        drop("POST", f"/jobs/{j}/cancel")
        cancelled = await resolve(project.jobs.cancel(j))
        assert cancelled.command.replayed
        try:
            await resolve(project.jobs.wait(j, timeout=60, initial_interval=0.05))
        except OperationFailedError as exc:
            assert exc.state == "cancelled"
        else:
            raise AssertionError("Cancelled job unexpectedly succeeded")
        j = controls["retry"]["job_id"]
        drop("POST", f"/jobs/{j}/retry")
        retried = await resolve(project.jobs.retry(j))
        assert retried.command.replayed and retried.command.retry_request_count == 1
        await resolve(project.jobs.wait(j, timeout=120, initial_interval=0.05))
        r = controls["delete"]["receipt_id"]
        assert (await resolve(project.deletions.get(r))).state.value == "failed"
        drop("POST", f"/document-deletions/{r}/retry")
        retried_deletion = await resolve(project.deletions.retry(r))
        assert (
            retried_deletion.command.replayed
            and retried_deletion.command.retry_request_count == 1
        )
        await resolve(project.deletions.wait(r, timeout=120, initial_interval=0.05))
        expired = controls["expired"]
        export = await resolve(
            project.documents.exports.get(expired["document_id"], expired["export_id"])
        )
        assert export.state.value == "expired"
        calls = await matrix(root, {**owner, **expired})
        assert await denied(calls[13], {409}) == "export_not_available"
        for d in created:
            key = uuid4().hex
            drop("DELETE", f"/documents/{d}")
            receipt = await resolve(project.documents.delete(d, idempotency_key=key))
            replay = await resolve(project.documents.delete(d, idempotency_key=key))
            assert receipt.id == replay.id
            await resolve(
                project.deletions.wait(receipt.id, timeout=120, initial_interval=0.05)
            )
            await denied(lambda d=d: project.documents.get(d), {404})
            assert not (
                await resolve(
                    project.search(
                        query=manifest["marker"],
                        filters=SearchFilters(document_ids=[UUID(d)]),
                    )
                )
            ).items
            cleanup.append(
                {"document_id": d, "receipt_id": str(receipt.id), "status": "deleted"}
            )
        created.clear()
        check(
            "timeout/resume, cancellation, failed-job retry, expired export, failed-deletion retry, final erasure"
        )
        expected = {name for _, _, name in evidence.operations}
        assert evidence.success == expected, (
            f"Missing successful operations: {expected - evidence.success}"
        )
        assert len(evidence.denials["foreign_project"]) == 25
        assert len(evidence.denials["missing_scope"]) == 25
        assert len(set(evidence.dropped)) == 9, "Missing lost-response mutation class"
        report.update(
            status="passed",
            successful_operations=sorted(evidence.success),
            denials={k: sorted(v) for k, v in evidence.denials.items()},
            lost_response_operations=sorted(set(evidence.dropped)),
        )
    finally:
        evidence.phase = "cleanup"
        for record in intakes:
            if "document_id" not in record:
                try:
                    state = await resolve(project.uploads.get(record["upload_id"]))
                    if state.document_id is not None:
                        record["document_id"] = str(state.document_id)
                        created.append(str(state.document_id))
                    else:
                        record["cleanup"] = (
                            "unfinalized_upload_requires_fixture_teardown_or_expiry"
                        )
                except Exception as exc:
                    record["cleanup_error_type"] = type(exc).__name__
        for d in created:
            try:
                receipt = await resolve(project.documents.delete(d))
                await resolve(
                    project.deletions.wait(
                        receipt.id, timeout=60, initial_interval=0.05
                    )
                )
                cleanup.append(
                    {
                        "document_id": d,
                        "receipt_id": str(receipt.id),
                        "status": "deleted",
                    }
                )
            except Exception as exc:
                cleanup.append(
                    {
                        "document_id": d,
                        "status": "failed",
                        "error_type": type(exc).__name__,
                    }
                )
        await close(root)


async def execute(args: argparse.Namespace) -> int:
    report: dict[str, Any] = {"status": "failed", "styles": {}}
    try:
        identity, contract = installed_identity(args.wheel)
        manifest = json.loads(args.manifest.read_text())
        private = Path(os.environ["RAGWELL_QUALIFICATION_CREDENTIALS_FILE"])
        if os.name == "posix" and private.stat().st_mode & 0o077:
            raise ValueError("Credentials file must be private (0600)")
        credentials = json.loads(private.read_text())
        report.update(
            identity,
            fixture_revision=manifest["fixture_revision"],
            api_commit=manifest["api_commit"],
            configuration=manifest["configuration"],
            manifest_sha256=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        )
        with httpx.Client(trust_env=False, timeout=30) as http:
            response = http.get(manifest["base_url"] + "/openapi.json")
            response.raise_for_status()
            observed = hashlib.sha256(
                service_projection(
                    response.json(), contract["x-ragwell-artifact-version"]
                )
            ).hexdigest()
        assert observed == identity["machine_sha256"] == manifest["machine_sha256"], (
            "Running API contract mismatch"
        )
        report["runtime_contract_sha256"] = observed
        for style in ("sync", "async"):
            report["styles"][style] = {}
            await run_style(
                style, manifest, credentials, contract, report["styles"][style]
            )
        report["status"] = "passed"
        return 0
    except Exception as exc:
        report["error_type"] = type(exc).__name__
        if isinstance(exc, ApiError):
            report["error_code"] = exc.code
            print("API failure code:", exc.code, file=sys.stderr)
        for result in report["styles"].values():
            if result.get("status") == "running":
                result["status"] = "failed"
        if hasattr(exc, "error_code"):
            print("Job failure code:", exc.error_code, file=sys.stderr)
        import traceback

        traceback.print_tb(exc.__traceback__)
        # Keep terminal diagnostics useful without including arbitrary exception bodies.
        print(f"Qualification failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    finally:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(asyncio.run(execute(parser.parse_args())))


if __name__ == "__main__":
    main()
