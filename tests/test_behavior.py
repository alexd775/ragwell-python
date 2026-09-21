"""Deterministic failure, recovery, ownership, and confidentiality qualification."""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from ragwell import (
    AsyncRagwell,
    ConfigurationError,
    ConflictError,
    DownloadIntegrityError,
    ProtocolError,
    QuotaExceededError,
    Ragwell,
    ServerError,
    ValidationError,
    WaitTimeoutError,
)
from ragwell.types import (
    DocumentExportPartResponse,
    RetrievalItemResponse,
    SearchRequest,
)

from ._fixtures import (
    DOCUMENT_ID,
    EXPORT_BYTES,
    EXPORT_ID,
    JOB_ID,
    PROJECT_ID,
    RecordingAPI,
    job,
    project,
)


def test_configuration_is_explicit_validated_and_redacted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RAGWELL_BASE_URL", raising=False)
    monkeypatch.delenv("RAGWELL_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="base_url"):
        Ragwell()
    with pytest.raises(ConfigurationError, match="loopback"):
        Ragwell(base_url="http://api.example.test", api_key="secret-value")
    with pytest.raises(ConfigurationError, match="credentials"):
        Ragwell(base_url="https://user:pass@example.test", api_key="secret-value")
    with pytest.raises(ConfigurationError, match="query"):
        Ragwell(base_url="https://example.test?secret=yes", api_key="secret-value")

    monkeypatch.setenv("RAGWELL_BASE_URL", "https://environment.example.test")
    monkeypatch.setenv("RAGWELL_API_KEY", "environment-secret")
    with Ragwell(
        base_url="https://explicit.example.test", api_key="explicit-secret"
    ) as client:
        representation = repr(client)
        assert "explicit.example.test" in representation
        assert "explicit-secret" not in representation
        assert "environment-secret" not in representation


def test_injected_sync_client_is_borrowed_by_default() -> None:
    injected = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(500))
    )
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        http_client=injected,
    ):
        pass
    assert not injected.is_closed
    injected.close()


def test_validation_error_preserves_safe_diagnostics_without_raw_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={
                "error": {
                    "code": "invalid_request",
                    "message": "Request validation failed",
                    "field_errors": [
                        {
                            "path": ["body", "query"],
                            "code": "string_too_short",
                            "message": "Value is too short",
                        }
                    ],
                }
            },
            headers={"X-Request-ID": "request-123", "Retry-After": "7"},
        )

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(ValidationError) as captured:
            client.project(PROJECT_ID).get()
    error = captured.value
    assert error.status_code == 422
    assert error.code == "invalid_request"
    assert error.request_id == "request-123"
    assert error.retry_after == 7
    assert error.field_errors[0].path == ["body", "query"]
    assert "body" not in repr(error)


def test_quota_is_not_retried_and_search_never_replays() -> None:
    calls = 0

    def quota(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            429,
            json={
                "error": {
                    "code": "plan_limit_exceeded",
                    "message": "Plan limit reached",
                    "limit_key": "successful_searches",
                    "unit": "search_units",
                    "limit": 10,
                    "used": 10,
                    "reserved": 0,
                    "requested": 1,
                    "remaining": 0,
                    "reset_at": None,
                }
            },
            headers={"Retry-After": "1"},
        )

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(quota),
    ) as client:
        with pytest.raises(QuotaExceededError) as captured:
            client.project(PROJECT_ID).search(query="do not replay")
    assert calls == 1
    assert captured.value.quota is not None
    assert captured.value.quota.remaining == 0

    calls = 0

    def unavailable(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            503,
            json={"error": {"code": "temporarily_unavailable", "message": "Try later"}},
        )

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(unavailable),
    ) as client:
        with pytest.raises(ServerError):
            client.project(PROJECT_ID).search(query="still no replay")
    assert calls == 1


def test_replayable_command_reuses_one_key_and_honors_retry_after() -> None:
    keys: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        keys.append(request.headers["Idempotency-Key"])
        if len(keys) == 1:
            return httpx.Response(
                429,
                json={
                    "error": {
                        "code": "command_in_progress",
                        "message": "Command is in progress",
                    }
                },
                headers={"Retry-After": "0"},
            )
        return httpx.Response(200, json=job())

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        result = client.project(PROJECT_ID).jobs.retry(JOB_ID)
    assert result.status.value == "succeeded"
    assert len(keys) == 2
    assert keys[0] == keys[1]


def test_lost_response_replay_keeps_the_same_command_identity() -> None:
    keys: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        keys.append(request.headers["Idempotency-Key"])
        if len(keys) == 1:
            raise httpx.ReadError("synthetic lost response", request=request)
        return httpx.Response(200, json=job())

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        client.project(PROJECT_ID).jobs.cancel(JOB_ID)
    assert len(keys) == 2
    assert keys[0] == keys[1]


def test_safe_read_retries_but_non_json_failure_stays_bounded() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                503,
                json={
                    "error": {
                        "code": "temporarily_unavailable",
                        "message": "Try later",
                    }
                },
                headers={"Retry-After": "0"},
            )
        return httpx.Response(200, json=project())

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        assert client.project(PROJECT_ID).get().id.hex.endswith("1")
    assert calls == 2

    def html_proxy(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, content=b"<html>private proxy diagnostic</html>")

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(html_proxy),
    ) as client:
        with pytest.raises(ServerError) as captured:
            client.project(PROJECT_ID).search(query="private query")
    assert "proxy diagnostic" not in str(captured.value)
    assert "private query" not in str(captured.value)


def test_wait_timeout_can_resume_without_remote_cancellation() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        state = "running" if len(requests) == 1 else "succeeded"
        return httpx.Response(200, json=job(state))

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        clock = [0.0]
        client._transport.monotonic = lambda: clock[0]
        client._transport.sleep = lambda seconds: clock.__setitem__(
            0, clock[0] + seconds
        )
        jobs = client.project(PROJECT_ID).jobs
        with pytest.raises(WaitTimeoutError) as captured:
            jobs.wait(JOB_ID, timeout=0)
        assert not requests
        assert captured.value.identifiers["job_id"] == JOB_ID
        with pytest.raises(WaitTimeoutError):
            jobs.wait(JOB_ID, timeout=1)
        assert jobs.wait(JOB_ID, timeout=1).status.value == "succeeded"
    assert [request.method for request in requests] == ["GET", "GET"]
    assert all(not request.url.path.endswith("/cancel") for request in requests)


def test_async_wait_cancellation_is_local_only() -> None:
    async def exercise() -> None:
        observed = asyncio.Event()
        requests: list[httpx.Request] = []

        async def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            observed.set()
            return httpx.Response(200, json=job("running"))

        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(handler),
        ) as client:
            task = asyncio.create_task(
                client.project(PROJECT_ID).jobs.wait(
                    JOB_ID, timeout=30, initial_interval=10
                )
            )
            await observed.wait()
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert [request.method for request in requests] == ["GET"]

    asyncio.run(exercise())


def test_job_cursor_is_opaque_and_repeated_cursor_is_rejected() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        assert request.url.params.get("after") in {None, "opaque.v1.cursor"}
        return httpx.Response(
            200, json={"items": [job()], "next_cursor": "opaque.v1.cursor"}
        )

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        iterator = client.project(PROJECT_ID).jobs.iter(limit=1)
        assert next(iterator).id.hex.endswith("4")
        with pytest.raises(ProtocolError, match="repeated"):
            next(iterator)
    assert calls == 2


@pytest.mark.parametrize(
    ("media_type", "payload"),
    [
        ("application/pdf", b"%PDF-synthetic"),
        ("text/plain", b"plain synthetic"),
        ("text/markdown", b"# synthetic"),
    ],
)
def test_sync_raw_upload_preserves_each_media_type(
    media_type: str, payload: bytes
) -> None:
    api = RecordingAPI()
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.sync),
    ) as client:
        client.project(PROJECT_ID).uploads.upload_content(
            "00000000-0000-0000-0000-000000000005",
            content=payload,
            content_type=media_type,
        )
    request = api.requests[0]
    assert request.headers["Content-Type"] == media_type
    assert request.content == payload


@pytest.mark.parametrize(
    ("media_type", "payload"),
    [
        ("application/pdf", b"%PDF-async"),
        ("text/plain", b"plain async"),
        ("text/markdown", b"# async"),
    ],
)
def test_async_raw_upload_preserves_each_media_type(
    media_type: str, payload: bytes
) -> None:
    async def exercise() -> None:
        api = RecordingAPI()
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(api.async_),
        ) as client:
            await client.project(PROJECT_ID).uploads.upload_content(
                "00000000-0000-0000-0000-000000000005",
                content=payload,
                content_type=media_type,
            )
        request = api.requests[0]
        assert request.headers["Content-Type"] == media_type
        assert request.content == payload

    asyncio.run(exercise())


def test_high_level_upload_restores_caller_cursor_and_does_not_close() -> None:
    api = RecordingAPI()
    stream = io.BytesIO(b"xxsynthetic")
    stream.seek(2)
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.sync),
    ) as client:
        result = client.project(PROJECT_ID).documents.upload(
            file=stream,
            filename="guide.txt",
            idempotency_key="upload-workflow-key",
        )
    assert result.job_id.hex.endswith("4")
    assert not stream.closed
    assert stream.tell() == 2
    create_body = json.loads(api.requests[0].content)
    assert create_body["declared_size_bytes"] == len(b"synthetic")
    assert create_body["declared_sha256"] == hashlib.sha256(b"synthetic").hexdigest()
    assert api.requests[1].content == b"synthetic"


def test_upload_and_all_wait_helpers_observe_without_extra_commands() -> None:
    api = RecordingAPI()
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.sync),
    ) as client:
        project_handle = client.project(PROJECT_ID)
        completed = project_handle.documents.upload_and_wait(
            file=b"synthetic",
            filename="guide.txt",
            idempotency_key="wait-upload-key",
        )
        deletion = project_handle.deletions.wait("00000000-0000-0000-0000-000000000006")
        exported = project_handle.documents.exports.wait(DOCUMENT_ID, EXPORT_ID)
    assert completed.job.status.value == "succeeded"
    assert deletion.state.value == "completed"
    assert exported.state.value == "succeeded"
    methods_and_paths = {(request.method, request.url.path) for request in api.requests}
    assert all(
        method == "GET" for method, path in methods_and_paths if path.endswith(JOB_ID)
    )
    assert not any(path.endswith("/cancel") for _, path in methods_and_paths)
    assert not any(path.endswith("/retry") for _, path in methods_and_paths)


def test_upload_mutation_surfaces_server_checksum_failure_and_restores_cursor() -> None:
    stream = io.BytesIO(b"synthetic")
    requests: list[httpx.Request] = []
    api = RecordingAPI()

    def handler(request: httpx.Request) -> httpx.Response:
        request.read()
        requests.append(request)
        if request.method == "POST" and request.url.path.endswith("/uploads"):
            stream.seek(0)
            stream.write(b"mutated!!")
            stream.seek(0)
            return api._respond(request)
        if request.method == "PUT" and request.url.path.endswith("/content"):
            return httpx.Response(
                409,
                json={
                    "error": {
                        "code": "upload_content_mismatch",
                        "message": "Content does not match the declaration",
                    }
                },
            )
        return api._respond(request)

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(ConflictError) as captured:
            client.project(PROJECT_ID).documents.upload(
                file=stream,
                filename="guide.txt",
                idempotency_key="mutation-upload-key",
            )
    assert captured.value.identifiers["upload_id"].endswith("5")
    assert stream.tell() == 0


def test_verified_download_is_atomic_and_rejects_partial_content(
    tmp_path: Path,
) -> None:
    part = DocumentExportPartResponse(
        part_number=0,
        byte_size=len(EXPORT_BYTES),
        sha256=hashlib.sha256(EXPORT_BYTES).hexdigest(),
    )
    destination = tmp_path / "part.ndjson"
    api = RecordingAPI()
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.sync),
    ) as client:
        saved = client.project(PROJECT_ID).documents.exports.download_part(
            DOCUMENT_ID, EXPORT_ID, part, destination
        )
    assert saved.path == destination
    assert destination.read_bytes() == EXPORT_BYTES
    assert not list(tmp_path.glob("*.part"))

    corrupt = DocumentExportPartResponse(
        part_number=0,
        byte_size=len(EXPORT_BYTES) + 1,
        sha256="0" * 64,
    )
    failed_destination = tmp_path / "corrupt.ndjson"
    api = RecordingAPI()
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.sync),
    ) as client:
        with pytest.raises(DownloadIntegrityError):
            client.project(PROJECT_ID).documents.exports.download_part(
                DOCUMENT_ID, EXPORT_ID, corrupt, failed_destination
            )
    assert not failed_destination.exists()


def test_async_upload_ownership_and_verified_download(tmp_path: Path) -> None:
    async def exercise() -> None:
        api = RecordingAPI()
        source = io.BytesIO(b"xxsynthetic")
        source.seek(2)
        destination = tmp_path / "async.ndjson"
        part = DocumentExportPartResponse(
            part_number=0,
            byte_size=len(EXPORT_BYTES),
            sha256=hashlib.sha256(EXPORT_BYTES).hexdigest(),
        )
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(api.async_),
        ) as client:
            project_handle = client.project(PROJECT_ID)
            result = await project_handle.documents.upload(
                file=source,
                filename="guide.txt",
                idempotency_key="async-upload-key",
            )
            saved = await project_handle.documents.exports.download_part(
                DOCUMENT_ID, EXPORT_ID, part, destination
            )
        assert result.job_id.hex.endswith("4")
        assert not source.closed
        assert source.tell() == 2
        assert saved.path == destination
        assert destination.read_bytes() == EXPORT_BYTES

    asyncio.run(exercise())


def test_omission_null_nullable_provenance_and_unknown_state() -> None:
    omitted = SearchRequest(query="synthetic").to_dict()
    explicit_null = SearchRequest(query="synthetic", filters=None).to_dict()
    assert "filters" not in omitted
    assert explicit_null["filters"] is None

    base: dict[str, Any] = {
        "rank": 1,
        "chunk_id": "00000000-0000-0000-0000-00000000000a",
        "document_id": DOCUMENT_ID,
        "document_version_id": "00000000-0000-0000-0000-000000000003",
        "content": "synthetic",
        "source_filename": "guide.txt",
        "representation_version": "rep-v1",
        "parts": [],
        "scores": {"text": None, "vector": 0.8, "final": 0.8},
    }
    page = RetrievalItemResponse.from_dict(
        {
            **base,
            "citation": {
                "kind": "page",
                "source_filename": "guide.pdf",
                "page_number": 1,
                "start_offset": 0,
                "end_offset": 9,
            },
        }
    )
    text = RetrievalItemResponse.from_dict(
        {
            **base,
            "citation": {
                "kind": "text",
                "source_filename": "guide.txt",
                "start_line": 1,
                "end_line": 1,
                "start_offset": 0,
                "end_offset": 9,
            },
        }
    )
    none = RetrievalItemResponse.from_dict({**base, "citation": None})
    assert page.citation is not None and page.citation.kind == "page"
    assert text.citation is not None and text.citation.kind == "text"
    assert none.citation is None

    def unknown(request: httpx.Request) -> httpx.Response:
        payload = job()
        payload["status"] = "future_state"
        return httpx.Response(200, json=payload)

    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(unknown),
    ) as client:
        with pytest.raises(ProtocolError):
            client.project(PROJECT_ID).jobs.get(JOB_ID)
