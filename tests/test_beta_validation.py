"""Offline beta-runner checks: real SDK HTTP calls, cleanup and evidence guards."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
import pytest

from qualification import beta_runner as beta
from ragwell import AsyncRagwell, Ragwell

from ._fixtures import (
    CHUNK_ID,
    DOCUMENT_ID,
    EXPORT_BYTES,
    PROJECT_ID,
    RETRIEVAL_ID,
    UPLOAD_ID,
    VERSION_ID,
    RecordingAPI,
    export,
    upload,
)


class BetaAPI(RecordingAPI):
    def __init__(self, fault: str = "") -> None:
        super().__init__()
        self.fault = fault
        self.content = b""
        self.deleted = False
        self.delete_calls = 0
        self.search_calls = 0
        self.recovery_calls = 0

    def _respond(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if (
            path.endswith("/uploads")
            and request.method == "POST"
            and self.fault == "lost_create"
        ):
            raise httpx.ReadError("secret-response-content", request=request)
        if (
            path.endswith("/uploads")
            and request.method == "POST"
            and self.fault in {"lost_finalize", "unfinalized"}
        ):
            value = upload()
            value.update(
                state="pending", document_id=None, document_version_id=None, job_id=None
            )
            return httpx.Response(201, json=value)
        if path.endswith(f"/uploads/{UPLOAD_ID}/content"):
            self.content = request.content
        if path.endswith(f"/uploads/{UPLOAD_ID}/finalize") and self.fault in {
            "lost_finalize",
            "unfinalized",
        }:
            self.requests.append(request)
            raise httpx.ReadError("secret-response-content", request=request)
        if path.endswith(f"/uploads/{UPLOAD_ID}") and request.method == "GET":
            self.recovery_calls += 1
            if self.fault == "unfinalized":
                value = upload()
                value.update(
                    state="uploaded",
                    document_id=None,
                    document_version_id=None,
                    job_id=None,
                )
                return httpx.Response(200, json=value)
        if path.endswith("/search"):
            self.requests.append(request)
            self.search_calls += 1
            if self.fault == "interrupted":
                raise asyncio.CancelledError()
            assert json.loads(request.content)["filters"]["document_ids"] == [
                DOCUMENT_ID
            ]
            if self.fault == "search_error":
                return httpx.Response(
                    403,
                    json={
                        "error": {
                            "code": "secret-code",
                            "message": "secret-response-content",
                        }
                    },
                )
            text = self.content.decode()
            return httpx.Response(
                200,
                json={
                    "retrieval_id": RETRIEVAL_ID,
                    "retrieval_version": "test-v1",
                    "profile_id": "test-v1",
                    "items": []
                    if self.fault == "empty_search"
                    else [
                        {
                            "chunk_id": CHUNK_ID,
                            "document_id": DOCUMENT_ID,
                            "document_version_id": VERSION_ID,
                            "content": text,
                            "source_filename": "synthetic.txt",
                            "rank": 1,
                            "representation_version": "test-v1",
                            "citation": {
                                "kind": "text",
                                "source_filename": "synthetic.txt",
                                "start_line": 1,
                                "end_line": 2,
                                "start_offset": 0,
                                "end_offset": len(text),
                            },
                            "parts": [{"kind": "evidence", "text": text}],
                            "scores": {
                                "final": 1.0,
                                "text": 1.0,
                                "vector": 1.0,
                            },
                        }
                    ],
                },
            )
        if request.method == "DELETE":
            self.delete_calls += 1
            assert path.endswith(f"/documents/{DOCUMENT_ID}")
            if self.fault == "cleanup_error":
                return httpx.Response(
                    403,
                    json={
                        "error": {
                            "code": "forbidden",
                            "message": "secret-response-content",
                        }
                    },
                )
            self.deleted = True
        if (
            self.deleted
            and path.endswith(f"/documents/{DOCUMENT_ID}")
            and request.method == "GET"
        ):
            return httpx.Response(
                404, json={"error": {"code": "not_found", "message": "Not found"}}
            )
        if (
            "/exports/" in path
            and self.fault == "export_tamper"
            and path.endswith("/parts/0")
        ):
            return httpx.Response(200, content=b"tampered")
        if self.fault == "huge_export" and "/exports/" in path:
            value = export()
            value["total_bytes"] = beta.MAX_EXPORT_BYTES + 1
            return httpx.Response(200, json=value)
        return super()._respond(request)


async def run_case(style: str, report: beta.Report, api: BetaAPI) -> bool:
    if style == "sync":
        with Ragwell(
            base_url="https://beta.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(api.sync),
        ) as client:
            return await beta.run_style(client, UUID(PROJECT_ID), style, report, 1)
    async with AsyncRagwell(
        base_url="https://beta.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.async_),
    ) as async_client:
        return await beta.run_style(async_client, UUID(PROJECT_ID), style, report, 1)


@pytest.mark.parametrize("style", ["sync", "async"])
@pytest.mark.parametrize(
    "fault",
    [
        "",
        "search_error",
        "empty_search",
        "lost_finalize",
        "export_tamper",
        "huge_export",
        "cleanup_error",
    ],
)
def test_lifecycle_and_failure_cleanup(style: str, fault: str, tmp_path: Path) -> None:
    report = beta.Report(tmp_path / "result.json")
    api = BetaAPI(fault)
    assert asyncio.run(run_case(style, report, api)) is (not fault)
    record = report.data["styles"][style]
    assert api.delete_calls == 1
    assert api.deleted is (fault != "cleanup_error")
    assert record["cleanup"]["status"] == (
        "failed" if fault == "cleanup_error" else "deleted"
    )
    assert record["status"] == ("failed" if fault else "passed")
    assert api.search_calls <= 1
    assert 0 < len(api.content) < 1024
    assert api.recovery_calls == (1 if fault == "lost_finalize" else 0)
    assert not any(request.url.path.endswith("/documents") for request in api.requests)
    saved = report.path.read_text()
    assert "test-key" not in saved and "secret-" not in saved
    assert api.content.decode() not in saved
    assert json.loads(saved)["qualification"] == "beta_lifecycle"
    if fault == "huge_export":
        assert not any("/parts/" in request.url.path for request in api.requests)
        assert record["error"]["check"] == "export_size"
    if fault == "export_tamper":
        assert record["error"]["error_type"] == "DownloadIntegrityError"
    if fault == "search_error":
        assert record["error"]["http_status"] == 403
    if fault == "empty_search":
        assert record["error"]["check"] == "retrieval_empty"
    if not fault:
        assert record["export_bytes"] == len(EXPORT_BYTES)


def test_report_is_exclusive_and_credentials_are_private(tmp_path: Path) -> None:
    path = tmp_path / "report.json"
    report = beta.Report(path)
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        beta.Report(path)
    assert path.read_bytes() == original
    key = tmp_path / "key"
    key.write_text("test-key\n")
    key.chmod(0o600)
    assert beta.read_key(key) == "test-key"
    if os.name == "posix":
        assert not path.stat().st_mode & 0o077
        key.chmod(0o644)
        with pytest.raises(beta.CheckFailed, match="permissions"):
            beta.read_key(key)
        key.chmod(0o600)
        link = tmp_path / "key-link"
        link.symlink_to(key)
        with pytest.raises(OSError):
            beta.read_key(link)
    key.write_text("line one\nline two")
    with pytest.raises(beta.CheckFailed, match="format"):
        beta.read_key(key)
    assert report.data["styles"]["async"]["status"] == "not_run"


@pytest.mark.parametrize(
    "url",
    [
        "http://beta.example.test",
        "https://u:p@beta.example.test",
        "https://beta.example.test?key=secret",
        "https://beta.example.test/v1",
    ],
)
def test_endpoint_rejects_unsafe_configuration(url: str) -> None:
    with pytest.raises(beta.CheckFailed):
        beta.endpoint(url)


def test_contract_mismatch_stops_before_credentials_and_mutations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = beta.Report(tmp_path / "report.json")
    monkeypatch.delenv("RAGWELL_BETA_API_KEY_FILE", raising=False)
    monkeypatch.setattr(
        beta, "installed_identity", lambda wheel: ({"machine_sha256": "expected"}, {})
    )
    monkeypatch.setattr(beta, "live_contract", lambda url, contract: "different")
    args = argparse.Namespace(
        base_url="https://beta.example.test",
        project_id=PROJECT_ID,
        wait_timeout=1,
        wheel=tmp_path / "wheel.whl",
    )
    assert asyncio.run(beta.execute(args, report)) == 1
    assert report.data["error"]["check"] == "running_contract_mismatch"
    assert all(value["status"] == "not_run" for value in report.data["styles"].values())


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), 601])
def test_invalid_deadlines_fail_before_network(timeout: float, tmp_path: Path) -> None:
    report = beta.Report(tmp_path / "report.json")
    args = argparse.Namespace(
        base_url="https://beta.example.test",
        project_id=PROJECT_ID,
        wait_timeout=timeout,
        wheel=tmp_path / "absent.whl",
    )
    assert asyncio.run(beta.execute(args, report)) == 1
    assert report.data["error"]["check"] == "wait_timeout_range"


def test_report_write_failure_does_not_skip_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = beta.Report(tmp_path / "report.json")
    api = BetaAPI()
    save = report.save

    def fail_after_upload() -> None:
        if report.data["styles"]["sync"].get("document_id"):
            raise OSError("secret-disk-error")
        save()

    monkeypatch.setattr(report, "save", fail_after_upload)
    with pytest.raises(OSError):
        asyncio.run(run_case("sync", report, api))
    assert api.delete_calls == 1 and api.deleted


@pytest.mark.parametrize("style", ["sync", "async"])
@pytest.mark.parametrize("fault", ["lost_create", "unfinalized"])
def test_incomplete_upload_is_reported_without_deleting_other_data(
    style: str, fault: str, tmp_path: Path
) -> None:
    report = beta.Report(tmp_path / "report.json")
    api = BetaAPI(fault)
    assert not asyncio.run(run_case(style, report, api))
    record = report.data["styles"][style]
    assert record["status"] == "failed" and api.delete_calls == 0
    assert record["cleanup"]["status"] == (
        "acceptance_unknown" if fault == "lost_create" else "upload_requires_expiry"
    )
    assert not any(request.url.path.endswith("/documents") for request in api.requests)


@pytest.mark.parametrize("style", ["sync", "async"])
def test_interruption_attempts_cleanup_and_remains_failure(
    style: str, tmp_path: Path
) -> None:
    report = beta.Report(tmp_path / "report.json")
    api = BetaAPI("interrupted")
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(run_case(style, report, api))
    record = report.data["styles"][style]
    assert record["status"] == "failed"
    assert record["cleanup"]["status"] == "deleted" and api.delete_calls == 1


@pytest.mark.parametrize("sync_failure", [False, True])
def test_execute_runs_both_clients_or_stops_on_first_failure(
    sync_failure: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = beta.Report(tmp_path / "report.json")
    key = tmp_path / "key"
    key.write_text("test-key")
    key.chmod(0o600)
    monkeypatch.setenv("RAGWELL_BETA_API_KEY_FILE", str(key))
    monkeypatch.setattr(
        beta, "installed_identity", lambda wheel: ({"machine_sha256": "same"}, {})
    )
    monkeypatch.setattr(beta, "live_contract", lambda url, contract: "same")
    calls: list[str] = []

    def sync_client(**kwargs: Any) -> Ragwell:
        calls.append("sync")
        return Ragwell(
            **kwargs,
            transport=httpx.MockTransport(
                BetaAPI("empty_search" if sync_failure else "").sync
            ),
        )

    def async_client(**kwargs: Any) -> AsyncRagwell:
        calls.append("async")
        return AsyncRagwell(**kwargs, transport=httpx.MockTransport(BetaAPI().async_))

    monkeypatch.setattr(beta, "Ragwell", sync_client)
    monkeypatch.setattr(beta, "AsyncRagwell", async_client)
    args = argparse.Namespace(
        base_url="https://beta.example.test",
        project_id=PROJECT_ID,
        wait_timeout=1,
        wheel=tmp_path / "candidate.whl",
    )
    assert asyncio.run(beta.execute(args, report)) == (1 if sync_failure else 0)
    assert calls == (["sync"] if sync_failure else ["sync", "async"])
    assert report.data["status"] == ("failed" if sync_failure else "passed")
    assert report.data["styles"]["async"]["status"] == (
        "not_run" if sync_failure else "passed"
    )
    assert "test-key" not in report.path.read_text()
