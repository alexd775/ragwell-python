"""Regressions for SDK-R1–R4, with synthetic content and deterministic clocks."""

from __future__ import annotations

import asyncio
import gzip
import hashlib
import inspect
import io
import json
import threading
import traceback
import zlib
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest

from ragwell import (
    AsyncRagwell,
    DownloadIntegrityError,
    OperationFailedError,
    PermissionDeniedError,
    ProtocolError,
    Ragwell,
    RagwellError,
    TransportError,
    TransportTimeout,
    WaitTimeoutError,
)
from ragwell.types import DocumentExportPartResponse

from ._fixtures import (
    DOCUMENT_ID,
    EXPORT_ID,
    JOB_ID,
    PROJECT_ID,
    RECEIPT_ID,
    UPLOAD_ID,
    VERSION_ID,
    RecordingAPI,
    deletion,
    export,
    job,
    project,
)


class Clock:
    now = 0.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


async def result(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def run(
    asynchronous: bool,
    handler: Callable[[httpx.Request], httpx.Response],
    exercise: Callable[[Any, Clock], Awaitable[None]],
    **configuration: Any,
) -> None:
    async def main() -> None:
        client: Any = (AsyncRagwell if asynchronous else Ragwell)(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(handler),
            **configuration,
        )
        clock = Clock()
        client._transport.monotonic = clock
        if asynchronous:
            client._transport._sleep = clock.sleep
        else:
            client._transport.sleep = clock.sleep
        try:
            await exercise(client, clock)
        finally:
            await result(client.aclose() if asynchronous else client.close())

    asyncio.run(main())


class Body(httpx.SyncByteStream, httpx.AsyncByteStream):
    def __init__(
        self,
        chunks: list[bytes],
        *,
        step: Callable[[], None] = lambda: None,
        fail: bool = False,
    ) -> None:
        self.chunks, self.step, self.fail = chunks, step, fail
        self.reads = 0
        self.closed = False

    def __iter__(self) -> Iterator[bytes]:
        for chunk in self.chunks:
            self.step()
            self.reads += 1
            yield chunk
        if self.fail:
            raise httpx.ReadError("synthetic-private-body-or-url")

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self:
            yield chunk

    def close(self) -> None:
        self.closed = True

    async def aclose(self) -> None:
        self.close()


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("resource", ["job", "deletion", "export"])
@pytest.mark.parametrize("scenario", ["zero", "late", "queued"])
def test_wait_deadline_covers_every_poll(
    asynchronous: bool,
    resource: str,
    scenario: str,
) -> None:
    calls: list[httpx.Request] = []
    clock = Clock()

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.extensions["timeout"]["read"] <= 1
        if scenario == "late":
            clock.sleep(10)
        payload = {
            "job": job("running" if scenario == "queued" else "succeeded"),
            "deletion": deletion("pending" if scenario == "queued" else "completed"),
            "export": export("queued" if scenario == "queued" else "succeeded"),
        }[resource]
        return httpx.Response(200, json=payload)

    async def exercise(client: Any, actual_clock: Clock) -> None:
        nonlocal clock
        clock = actual_clock
        p = client.project(PROJECT_ID)
        with pytest.raises(WaitTimeoutError) as failure:
            if resource == "job":
                await result(
                    p.jobs.wait(JOB_ID, timeout=0 if scenario == "zero" else 1)
                )
            elif resource == "deletion":
                await result(
                    p.deletions.wait(RECEIPT_ID, timeout=0 if scenario == "zero" else 1)
                )
            else:
                await result(
                    p.documents.exports.wait(
                        DOCUMENT_ID, EXPORT_ID, timeout=0 if scenario == "zero" else 1
                    )
                )
        assert failure.value.identifiers["project_id"] == PROJECT_ID
        assert len(calls) == (0 if scenario == "zero" else 1)
        assert all(r.method == "GET" for r in calls)
        assert client._transport._budget.get() is None

    run(asynchronous, handler, exercise)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.0])
def test_invalid_durations_fail_before_network(
    asynchronous: bool, value: float
) -> None:
    cls = AsyncRagwell if asynchronous else Ragwell
    for name in ("operation_timeout", "transfer_timeout"):
        options: dict[str, Any] = {name: value}
        with pytest.raises(ValueError, match="finite"):
            cls(base_url="https://api.example.test", api_key="test-key", **options)

    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail("invalid upload-and-wait settings must not create an upload")

    async def exercise(client: Any, clock: Clock) -> None:
        for options in ({"wait_timeout": value}, {"initial_interval": value}):
            with pytest.raises(ValueError, match="finite"):
                await result(
                    client.project(PROJECT_ID).documents.upload_and_wait(
                        file=b"synthetic", filename="guide.txt", **options
                    )
                )

    run(asynchronous, handler, exercise)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("status", [200, 403])
@pytest.mark.parametrize("encoding", ["identity", "gzip", "deflate"])
def test_body_caps_apply_during_reads_and_decompression(
    asynchronous: bool,
    status: int,
    encoding: str,
) -> None:
    limit = 16_777_216 if status == 200 else 1_048_576
    chunk = b"x" * 65536
    if encoding == "identity":
        chunks = [chunk] * (limit // len(chunk) + 20)
    else:
        compressor = zlib.compressobj(wbits=31 if encoding == "gzip" else 15)
        compressed = (
            b"".join(
                compressor.compress(chunk) for _ in range(limit // len(chunk) + 20)
            )
            + compressor.flush()
        )
        chunks = [compressed, b"unread synthetic tail"]
    body = Body(chunks)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status,
            stream=body,
            headers={
                "content-encoding": encoding,
                "content-length": "1",
                "X-Request-ID": "safe-request",
            },
        )

    async def exercise(client: Any, clock: Clock) -> None:
        with pytest.raises(ProtocolError, match="bounded") as failure:
            await result(client.project(PROJECT_ID).get())
        assert body.closed
        assert body.reads < len(chunks)
        assert failure.value.request_id == "safe-request"

    run(asynchronous, handler, exercise)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("encoding", ["identity", "gzip", "deflate"])
def test_bounded_decoder_preserves_valid_payloads(
    asynchronous: bool, encoding: str
) -> None:
    payload = json.dumps(project()).encode()
    encoded = (
        payload
        if encoding == "identity"
        else (gzip.compress(payload) if encoding == "gzip" else zlib.compress(payload))
    )
    body = Body([encoded[i : i + 7] for i in range(0, len(encoded), 7)])

    async def exercise(client: Any, clock: Clock) -> None:
        parsed = await result(client.project(PROJECT_ID).get())
        assert str(parsed.id) == PROJECT_ID
        assert body.closed

    run(
        asynchronous,
        lambda request: httpx.Response(
            200, stream=body, headers={"content-encoding": encoding}
        ),
        exercise,
    )


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("streaming", [False, True])
def test_deadline_runs_through_slow_body(asynchronous: bool, streaming: bool) -> None:
    clock = Clock()
    body = Body([b"a", b"b", b"c"], step=lambda: clock.sleep(0.6))

    async def exercise(client: Any, actual_clock: Clock) -> None:
        nonlocal clock
        clock = actual_clock
        with pytest.raises(TransportTimeout):
            if streaming:
                stream = await result(
                    client.project(PROJECT_ID).documents.exports.stream_part(
                        DOCUMENT_ID, EXPORT_ID, 0
                    )
                )
                if asynchronous:
                    async for _ in stream.iter_bytes():
                        pass
                else:
                    list(stream.iter_bytes())
            else:
                await result(client.project(PROJECT_ID).get())
        assert body.closed
        assert body.reads == 2

    run(
        asynchronous,
        lambda request: httpx.Response(200, stream=body),
        exercise,
        operation_timeout=1,
        transfer_timeout=1,
    )


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("scenario", ["oversize", "interrupted", "deadline"])
def test_download_stops_and_preserves_destination(
    asynchronous: bool,
    scenario: str,
    tmp_path: Path,
) -> None:
    clock = Clock()
    body = Body(
        [b"ab", b"cd", b"ef", b"gh"],
        step=lambda: clock.sleep(0.6 if scenario == "deadline" else 0),
        fail=scenario == "interrupted",
    )
    destination = tmp_path / "export.ndjson"
    destination.write_bytes(b"original")
    part = DocumentExportPartResponse(
        part_number=0,
        byte_size=3 if scenario == "oversize" else 8,
        sha256=hashlib.sha256(b"abcdefgh").hexdigest(),
    )

    async def exercise(client: Any, actual_clock: Clock) -> None:
        nonlocal clock
        clock = actual_clock
        error_type = {
            "oversize": DownloadIntegrityError,
            "interrupted": TransportError,
            "deadline": TransportTimeout,
        }[scenario]
        with pytest.raises(error_type):
            await result(
                client.project(PROJECT_ID).documents.exports.download_part(
                    DOCUMENT_ID, EXPORT_ID, part, destination, overwrite=True
                )
            )
        assert destination.read_bytes() == b"original"
        assert list(tmp_path.iterdir()) == [destination]
        assert body.closed
        if scenario != "interrupted":
            assert body.reads == 2

    run(
        asynchronous,
        lambda request: httpx.Response(200, stream=body),
        exercise,
        transfer_timeout=1,
    )


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "failure_kind", ["permission", "transport", "protocol", "failed", "timeout"]
)
def test_upload_retains_all_accepted_ids(asynchronous: bool, failure_kind: str) -> None:
    api = RecordingAPI()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if "/jobs/" in request.url.path:
            if failure_kind == "permission":
                return httpx.Response(
                    403,
                    json={"error": {"code": "forbidden", "message": "Not permitted"}},
                    headers={"X-Request-ID": "safe-request"},
                )
            if failure_kind == "transport":
                raise httpx.ReadError("synthetic-private-body-or-url")
            return httpx.Response(
                200,
                json=job(
                    {
                        "protocol": "synthetic-private-body-or-url",
                        "failed": "failed",
                        "timeout": "running",
                    }[failure_kind]
                ),
            )
        return api._respond(request)

    async def exercise(client: Any, clock: Clock) -> None:
        expected: type[RagwellError] = {
            "permission": PermissionDeniedError,
            "transport": TransportError,
            "protocol": ProtocolError,
            "failed": OperationFailedError,
            "timeout": WaitTimeoutError,
        }[failure_kind]
        with pytest.raises(expected) as failure:
            await result(
                client.project(PROJECT_ID).documents.upload_and_wait(
                    file=b"synthetic", filename="guide.txt", wait_timeout=2
                )
            )
        assert (
            failure.value.identifiers.items()
            >= {
                "project_id": PROJECT_ID,
                "upload_id": UPLOAD_ID,
                "document_id": DOCUMENT_ID,
                "version_id": VERSION_ID,
                "job_id": JOB_ID,
            }.items()
        )
        if failure_kind == "permission":
            assert failure.value.request_id == "safe-request"
        assert (
            len(
                [
                    r
                    for r in requests
                    if r.method == "POST" and r.url.path.endswith("/uploads")
                ]
            )
            == 1
        )
        text = (
            "".join(traceback.format_exception(failure.value))
            + str(failure.value)
            + repr(failure.value)
        )
        assert "synthetic-private-body-or-url" not in text

    run(asynchronous, handler, exercise)


@pytest.mark.parametrize("asynchronous", [False, True])
def test_upload_steps_share_budget_and_restore_input(asynchronous: bool) -> None:
    clock = Clock()
    api = RecordingAPI()
    stream = io.BytesIO(b"prefixsynthetic")
    stream.seek(6)

    def handler(request: httpx.Request) -> httpx.Response:
        clock.sleep(0.6)
        return api._respond(request)

    async def exercise(client: Any, actual_clock: Clock) -> None:
        nonlocal clock
        clock = actual_clock
        with pytest.raises(TransportTimeout) as failure:
            await result(
                client.project(PROJECT_ID).documents.upload(
                    file=stream, filename="guide.txt"
                )
            )
        assert failure.value.identifiers["upload_id"] == UPLOAD_ID
        assert stream.tell() == 6 and not stream.closed
        assert len(api.requests) == 2  # no finalize with a fresh transfer budget

    run(asynchronous, handler, exercise, transfer_timeout=1)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("field", ["id", "created_at", "status", "json", "stream"])
def test_malformed_and_stream_failures_have_safe_traces(
    asynchronous: bool, field: str
) -> None:
    marker = "synthetic-private-body-or-url"
    payload = job()
    body = Body([b"{}"], fail=True)

    def handler(request: httpx.Request) -> httpx.Response:
        if field == "stream":
            return httpx.Response(
                200, stream=body, headers={"X-Request-ID": "safe-request"}
            )
        if field == "json":
            return httpx.Response(
                200,
                content=b'{"bad":' + marker.encode(),
                headers={"X-Request-ID": "safe-request"},
            )
        payload[field] = marker
        return httpx.Response(
            200, json=payload, headers={"X-Request-ID": "safe-request"}
        )

    async def exercise(client: Any, clock: Clock) -> None:
        with pytest.raises(RagwellError) as failure:
            if field == "stream":
                stream = await result(
                    client.project(PROJECT_ID).documents.exports.stream_part(
                        DOCUMENT_ID, EXPORT_ID, 0
                    )
                )
                if asynchronous:
                    async for _ in stream.iter_bytes():
                        pass
                else:
                    list(stream.iter_bytes())
            else:
                await result(client.project(PROJECT_ID).jobs.get(JOB_ID))
        assert failure.value.request_id == "safe-request"
        assert failure.value.operation_id
        text = (
            "".join(traceback.format_exception(failure.value))
            + str(failure.value)
            + repr(failure.value)
        )
        assert marker not in text
        if field == "stream":
            assert body.closed

    run(asynchronous, handler, exercise)


def test_async_cancellation_during_hash_restores_caller_cursor() -> None:
    entered, release = threading.Event(), threading.Event()

    class SlowFile(io.BytesIO):
        def read(self, size: int | None = -1) -> bytes:
            entered.set()
            assert release.wait(5)
            return super().read(size)

    stream = SlowFile(b"prefixsynthetic")
    stream.seek(6)

    async def exercise() -> None:
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(
                lambda request: pytest.fail("cancelled upload sent a request")
            ),
        ) as client:
            task = asyncio.create_task(
                client.project(PROJECT_ID).documents.upload(
                    file=stream, filename="guide.txt"
                )
            )
            try:
                assert await asyncio.to_thread(entered.wait, 5)
                task.cancel()
            finally:
                release.set()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert stream.tell() == 6 and not stream.closed

    asyncio.run(exercise())


@pytest.mark.parametrize("asynchronous", [False, True])
def test_command_retry_never_crosses_receipt_horizon(asynchronous: bool) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            429,
            headers={"Retry-After": "86400"},
            json={
                "error": {
                    "code": "command_in_progress",
                    "message": "Command in progress",
                }
            },
        )

    async def exercise(client: Any, clock: Clock) -> None:
        with pytest.raises(RagwellError):
            await result(client.project(PROJECT_ID).jobs.cancel(JOB_ID))
        assert calls == 1
        assert clock.now == 0

    run(asynchronous, handler, exercise, operation_timeout=500000)


@pytest.mark.parametrize("asynchronous", [False, True])
def test_wait_preserves_shorter_operation_timeout(asynchronous: bool) -> None:
    clock = Clock()

    def handler(request: httpx.Request) -> httpx.Response:
        clock.sleep(1)
        return httpx.Response(200, json=job())

    async def exercise(client: Any, actual_clock: Clock) -> None:
        nonlocal clock
        clock = actual_clock
        with pytest.raises(TransportTimeout):
            await result(client.project(PROJECT_ID).jobs.wait(JOB_ID, timeout=2))

    run(asynchronous, handler, exercise, operation_timeout=0.5)


@pytest.mark.parametrize("asynchronous", [False, True])
def test_hashing_is_inside_upload_deadline(asynchronous: bool) -> None:
    clock = Clock()

    class SlowHash(io.BytesIO):
        def read(self, size: int | None = -1) -> bytes:
            clock.sleep(2)
            return super().read(size)

    source = SlowHash(b"synthetic")

    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail("hashing exhausted the transfer budget before intake")

    async def exercise(client: Any, actual_clock: Clock) -> None:
        nonlocal clock
        clock = actual_clock
        with pytest.raises(TransportTimeout):
            await result(
                client.project(PROJECT_ID).documents.upload(
                    file=source, filename="guide.txt"
                )
            )
        assert source.tell() == 0 and not source.closed

    run(asynchronous, handler, exercise, transfer_timeout=1)


@pytest.mark.parametrize("phase", ["headers", "body"])
def test_default_sync_network_clips_each_read(
    phase: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import httpcore

    from ragwell import _sync_http

    clock = Clock()
    timeouts: list[float | None] = []
    headers = b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n"
    chunks = (
        [headers[:10], headers[10:20], headers[20:]]
        if phase == "headers"
        else [headers, b"a", b"b", b"c"]
    )

    class Socket(httpcore.MockStream):
        def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
            timeouts.append(timeout)
            clock.sleep(0.4)
            return super().read(max_bytes, timeout)

    class Backend(httpcore.MockBackend):
        def connect_tcp(
            self,
            host: str,
            port: int,
            timeout: float | None = None,
            local_address: str | None = None,
            socket_options: Any = None,
        ) -> httpcore.NetworkStream:
            return Socket(chunks)

    monkeypatch.setattr(_sync_http, "getproxies", lambda: {})
    transport = _sync_http.DeadlineHTTPTransport(
        httpx.URL("https://api.example.test"), verify=True, backend=Backend([])
    )
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=transport,
        operation_timeout=1,
    ) as client:
        client._transport.monotonic = clock
        with pytest.raises(TransportTimeout):
            client.project(PROJECT_ID).get()
    assert timeouts == pytest.approx([1.0, 0.6, 0.2])


def test_async_inflight_send_obeys_total_deadline() -> None:
    async def exercise() -> None:
        closed = asyncio.Event()

        async def handler(request: httpx.Request) -> httpx.Response:
            try:
                await asyncio.Future[None]()
                raise AssertionError("unreachable")
            finally:
                closed.set()

        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(handler),
            operation_timeout=0.01,
        ) as client:
            with pytest.raises(TransportTimeout):
                await client.project(PROJECT_ID).get()
        assert closed.is_set()

    asyncio.run(exercise())


def test_async_cancelled_download_closes_and_removes_temporary(tmp_path: Path) -> None:
    async def exercise() -> None:
        reading = asyncio.Event()

        class BlockedBody(httpx.AsyncByteStream):
            closed = False

            async def __aiter__(self) -> AsyncIterator[bytes]:
                yield b"ab"
                reading.set()
                await asyncio.Future[None]()

            async def aclose(self) -> None:
                self.closed = True

        body = BlockedBody()
        destination = tmp_path / "export.ndjson"
        part = DocumentExportPartResponse(part_number=0, byte_size=4, sha256="0" * 64)
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, stream=body)
            ),
        ) as client:
            task = asyncio.create_task(
                client.project(PROJECT_ID).documents.exports.download_part(
                    DOCUMENT_ID, EXPORT_ID, part, destination
                )
            )
            await asyncio.wait_for(reading.wait(), timeout=5)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert body.closed
        assert not list(tmp_path.iterdir())

    asyncio.run(exercise())


@pytest.mark.parametrize("asynchronous", [False, True])
def test_nested_provenance_decode_trace_is_safe(asynchronous: bool) -> None:
    marker = "synthetic-private-provenance"
    payload = {
        "items": [
            {
                "rank": 1,
                "chunk_id": JOB_ID,
                "document_id": DOCUMENT_ID,
                "document_version_id": VERSION_ID,
                "content": "synthetic",
                "source_filename": "guide.txt",
                "representation_version": "rep-v1",
                "parts": [{"kind": marker, "text": "synthetic", "source_id": JOB_ID}],
                "scores": {"text": None, "vector": 0.8, "final": 0.8},
                "citation": None,
            }
        ],
        "profile_id": None,
        "retrieval_id": JOB_ID,
        "retrieval_version": "v1",
    }

    async def exercise(client: Any, clock: Clock) -> None:
        with pytest.raises(ProtocolError) as failure:
            await result(client.project(PROJECT_ID).search(query="synthetic"))
        assert marker not in "".join(traceback.format_exception(failure.value))

    run(asynchronous, lambda request: httpx.Response(200, json=payload), exercise)


def test_default_sync_network_decodes_a_successful_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import httpcore

    from ragwell import _sync_http

    monkeypatch.setattr(_sync_http, "getproxies", lambda: {})
    payload = gzip.compress(json.dumps(project()).encode())
    wire = (
        b"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Length: "
        + str(len(payload)).encode()
        + b"\r\n\r\n"
        + payload
    )
    transport = _sync_http.DeadlineHTTPTransport(
        httpx.URL("https://api.example.test"),
        verify=True,
        backend=httpcore.MockBackend([wire]),
    )
    with Ragwell(
        base_url="https://api.example.test", api_key="test-key", transport=transport
    ) as client:
        assert str(client.project(PROJECT_ID).get().id) == PROJECT_ID


def test_cancellation_during_temporary_file_creation_cleans_up(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ragwell import async_client
    from ragwell._common import create_temporary_destination

    original = create_temporary_destination
    entered, release = threading.Event(), threading.Event()
    created: list[Any] = []

    def create(*args: Any, **kwargs: Any) -> Any:
        value = original(*args, **kwargs)
        created.append(value)
        entered.set()
        assert release.wait(5)
        return value

    monkeypatch.setattr(async_client, "create_temporary_destination", create)

    async def exercise() -> None:
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(
                lambda request: pytest.fail("no HTTP after cancellation")
            ),
        ) as client:
            task = asyncio.create_task(
                client.project(PROJECT_ID).documents.exports.download_part(
                    DOCUMENT_ID,
                    EXPORT_ID,
                    DocumentExportPartResponse(
                        part_number=0, byte_size=4, sha256="0" * 64
                    ),
                    tmp_path / "part",
                )
            )
            try:
                assert await asyncio.to_thread(entered.wait, 5)
                task.cancel()
                await asyncio.sleep(0)
                task.cancel()  # repeated cancellation must not lose the worker's handle
            finally:
                release.set()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert len(created) == 1 and created[0][0].closed
        assert not list(tmp_path.iterdir())

    asyncio.run(exercise())
