"""Every reviewed operation is reachable and exercised in both client styles."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx

from ragwell import AsyncRagwell, Ragwell
from ragwell.types import (
    CreateDocumentExportRequest,
    CreateUploadRequest,
    CreateUploadRequestDeclaredMediaType,
    DocumentMetadataInput,
    ReplaceDocumentMetadataRequest,
)

from ._fixtures import (
    DOCUMENT_ID,
    EXPORT_BYTES,
    EXPORT_ID,
    GENERATION_ID,
    JOB_ID,
    PROJECT_ID,
    RECEIPT_ID,
    SOURCE_ID,
    UPLOAD_ID,
    RecordingAPI,
)

ROOT = Path(__file__).resolve().parents[1]


def _operation_documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = json.loads((ROOT / "contracts/2026-09-19.1/manifest.json").read_text())
    mapping = json.loads((ROOT / "contracts/operations.json").read_text())
    openapi = json.loads((ROOT / "contracts/2026-09-19.1/openapi.json").read_text())
    return manifest, mapping, openapi


def _resolve_public_method(root: object, path: str) -> object:
    current = root
    for part in path.split(".")[1:]:
        current = getattr(current, part)
    return current


def test_vendored_digest_inventory_generated_and_public_mapping_are_complete() -> None:
    manifest, mapping, openapi = _operation_documents()
    digest = hashlib.sha256(
        (ROOT / "contracts/2026-09-19.1/openapi.json").read_bytes()
    ).hexdigest()
    assert digest == manifest["machine_sha256"] == mapping["machine_sha256"]
    assert manifest["operation_count"] == len(mapping["operations"]) == 26
    expected = {
        (item["method"], item["path"], item["operation_id"])
        for item in manifest["operations"]
    }
    mapped = {
        (item["method"], item["path"], item["operation_id"])
        for item in mapping["operations"]
    }
    actual = {
        (method.upper(), path, operation["operationId"])
        for path, path_item in openapi["paths"].items()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    }
    assert actual == mapped == expected

    generated = list((ROOT / "src/ragwell/_generated/api").glob("**/*.py"))
    assert len([path for path in generated if path.name != "__init__.py"]) == 26
    sync_source = (ROOT / "src/ragwell/client.py").read_text()
    async_source = (ROOT / "src/ragwell/async_client.py").read_text()
    for _, _, operation_id in expected:
        assert operation_id in sync_source
        assert operation_id in async_source

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(lambda request: httpx.Response(500)),
    ) as sync_client:
        sync_project = sync_client.project(PROJECT_ID)
        for item in mapping["operations"]:
            root = sync_client if item["sync"].startswith("client.") else sync_project
            assert callable(_resolve_public_method(root, item["sync"]))

    async def check_async() -> None:
        async def failure(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500)

        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(failure),
        ) as async_client:
            async_project = async_client.project(PROJECT_ID)
            for item in mapping["operations"]:
                root = (
                    async_client
                    if item["async"].startswith("client.")
                    else async_project
                )
                assert callable(_resolve_public_method(root, item["async"]))

    asyncio.run(check_async())


def _expected_wire_inventory() -> set[tuple[str, str]]:
    manifest, _, _ = _operation_documents()
    replacements = {
        "{project_id}": PROJECT_ID,
        "{document_id}": DOCUMENT_ID,
        "{receipt_id}": RECEIPT_ID,
        "{export_id}": EXPORT_ID,
        "{generation_id}": GENERATION_ID,
        "{source_id}": SOURCE_ID,
        "{job_id}": JOB_ID,
        "{upload_id}": UPLOAD_ID,
        "{part_number}": "0",
    }
    result: set[tuple[str, str]] = set()
    for item in manifest["operations"]:
        path = item["path"]
        for source, value in replacements.items():
            path = path.replace(source, value)
        result.add((item["method"], path))
    return result


def _request_models() -> tuple[
    CreateUploadRequest, ReplaceDocumentMetadataRequest, CreateDocumentExportRequest
]:
    create = CreateUploadRequest(
        original_filename="guide.txt",
        declared_media_type=CreateUploadRequestDeclaredMediaType.TEXTPLAIN,
        declared_size_bytes=9,
        declared_sha256=hashlib.sha256(b"synthetic").hexdigest(),
    )
    replace = ReplaceDocumentMetadataRequest(
        expected_revision=1, tags=["guide"], metadata=DocumentMetadataInput()
    )
    export = CreateDocumentExportRequest(generation_id=UUID(GENERATION_ID))
    return create, replace, export


def test_all_26_sync_operations_round_trip_exact_wire_shapes() -> None:
    api = RecordingAPI()
    create, replace, export_request = _request_models()
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.sync),
    ) as client:
        project = client.project(PROJECT_ID)
        assert client.upload_policy.get().formats
        assert project.get().id == UUID(PROJECT_ID)
        assert project.deletions.get(RECEIPT_ID).id == UUID(RECEIPT_ID)
        project.deletions.retry(RECEIPT_ID, idempotency_key="deletion-key")
        assert project.documents.list().items
        project.documents.delete(DOCUMENT_ID, idempotency_key="delete-key")
        project.documents.get(DOCUMENT_ID)
        project.documents.activity(DOCUMENT_ID)
        project.documents.exports.create(
            DOCUMENT_ID, export_request, idempotency_key="export-key"
        )
        export = project.documents.exports.get(DOCUMENT_ID, EXPORT_ID)
        with project.documents.exports.stream_part(DOCUMENT_ID, EXPORT_ID, 0) as stream:
            assert b"".join(stream.iter_bytes()) == EXPORT_BYTES
        project.documents.generations.list(DOCUMENT_ID)
        project.documents.chunks.list(DOCUMENT_ID, GENERATION_ID)
        project.documents.sources.get(DOCUMENT_ID, GENERATION_ID, SOURCE_ID)
        project.documents.inspect(DOCUMENT_ID)
        project.documents.replace_metadata(
            DOCUMENT_ID, replace, idempotency_key="metadata-key"
        )
        project.embedding_connection.get()
        project.jobs.list(status=[])
        project.jobs.get(JOB_ID)
        project.jobs.cancel(JOB_ID, idempotency_key="cancel-key")
        project.jobs.retry(JOB_ID, idempotency_key="retry-key")
        project.search(query="synthetic")
        project.uploads.create(create, idempotency_key="upload-key")
        recovered = project.uploads.get(UPLOAD_ID)
        assert recovered.additional_properties["additive_future_field"] == "preserved"
        project.uploads.upload_content(
            UPLOAD_ID, content=b"synthetic", content_type="text/plain"
        )
        project.uploads.finalize(UPLOAD_ID)
        assert export.parts[0].part_number == 0

    observed = {(request.method, request.url.path) for request in api.requests}
    assert len(api.requests) == 26
    assert observed == _expected_wire_inventory()


def test_all_26_async_operations_round_trip_exact_wire_shapes() -> None:
    async def exercise() -> None:
        api = RecordingAPI()
        create, replace, export_request = _request_models()
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(api.async_),
        ) as client:
            project = client.project(PROJECT_ID)
            assert (await client.upload_policy.get()).formats
            assert (await project.get()).id == UUID(PROJECT_ID)
            await project.deletions.get(RECEIPT_ID)
            await project.deletions.retry(RECEIPT_ID, idempotency_key="deletion-key")
            await project.documents.list()
            await project.documents.delete(DOCUMENT_ID, idempotency_key="delete-key")
            await project.documents.get(DOCUMENT_ID)
            await project.documents.activity(DOCUMENT_ID)
            await project.documents.exports.create(
                DOCUMENT_ID, export_request, idempotency_key="export-key"
            )
            await project.documents.exports.get(DOCUMENT_ID, EXPORT_ID)
            stream = await project.documents.exports.stream_part(
                DOCUMENT_ID, EXPORT_ID, 0
            )
            async with stream:
                content = b"".join([chunk async for chunk in stream.iter_bytes()])
                assert content == EXPORT_BYTES
            await project.documents.generations.list(DOCUMENT_ID)
            await project.documents.chunks.list(DOCUMENT_ID, GENERATION_ID)
            await project.documents.sources.get(DOCUMENT_ID, GENERATION_ID, SOURCE_ID)
            await project.documents.inspect(DOCUMENT_ID)
            await project.documents.replace_metadata(
                DOCUMENT_ID, replace, idempotency_key="metadata-key"
            )
            await project.embedding_connection.get()
            await project.jobs.list(status=[])
            await project.jobs.get(JOB_ID)
            await project.jobs.cancel(JOB_ID, idempotency_key="cancel-key")
            await project.jobs.retry(JOB_ID, idempotency_key="retry-key")
            await project.search(query="synthetic")
            await project.uploads.create(create, idempotency_key="upload-key")
            await project.uploads.get(UPLOAD_ID)
            await project.uploads.upload_content(
                UPLOAD_ID, content=b"synthetic", content_type="text/plain"
            )
            await project.uploads.finalize(UPLOAD_ID)

        observed = {(request.method, request.url.path) for request in api.requests}
        assert len(api.requests) == 26
        assert observed == _expected_wire_inventory()

    asyncio.run(exercise())
