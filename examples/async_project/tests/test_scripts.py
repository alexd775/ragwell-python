"""Exercise the example offline against the installed public SDK."""

import asyncio
import json
import subprocess
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import httpx
import pytest
from ragwell import AsyncRagwell, OperationFailedError, WaitTimeoutError
from ragwell.types import DocumentResponse, DocumentState

import clean_project
import common
import retrieve
import sync_documents

PROJECT_ID = UUID(int=1)
DOCUMENT_ID = UUID(int=2)
JOB_ID = UUID(int=3)
RECEIPT_ID = UUID(int=4)


def document(name="guide.txt", *, id=DOCUMENT_ID, state="ready"):
    return DocumentResponse.from_dict(
        {
            "id": str(id),
            "original_filename": name,
            "state": state,
            "metadata": {
                "source": None,
                "author": None,
                "language": None,
                "category": None,
            },
            "metadata_revision": 1,
            "tags": [],
            "created_at": "2026-09-22T00:00:00Z",
            "updated_at": "2026-09-22T00:00:00Z",
            "metadata_updated_at": "2026-09-22T00:00:00Z",
        }
    )


def project_fixture(initial=()):
    documents = list(initial)

    async def iter_documents() -> AsyncIterator[DocumentResponse]:
        for item in list(documents):
            yield item

    async def upload(*, file, media_type):
        item = document(file.name, id=UUID(int=len(documents) + 20))
        documents.append(item)
        return SimpleNamespace(document=item, job_id=JOB_ID)

    async def deletion_completed(receipt_id, *, timeout):
        # Tombstones may still be returned by the API after erasure.
        for item in documents:
            item.state = DocumentState.DELETED
        return SimpleNamespace(state="completed")

    project = SimpleNamespace(
        id=PROJECT_ID,
        documents=SimpleNamespace(
            iter=iter_documents,
            upload=AsyncMock(side_effect=upload),
            inspect=AsyncMock(
                return_value=SimpleNamespace(searchable=True, latest_job=None)
            ),
            delete=AsyncMock(return_value=SimpleNamespace(id=RECEIPT_ID)),
        ),
        jobs=SimpleNamespace(
            wait=AsyncMock(return_value=SimpleNamespace(status="succeeded"))
        ),
        deletions=SimpleNamespace(wait=AsyncMock(side_effect=deletion_completed)),
    )
    return project


def test_sync_adds_only_missing_filenames_and_rerun_skips(tmp_path, capsys):
    (tmp_path / "guide.txt").write_text("changed local content", encoding="utf-8")
    (tmp_path / "new.md").write_text("new document", encoding="utf-8")
    (tmp_path / "image.jpg").write_bytes(b"not a supported document")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "private.txt").write_text("not scanned", encoding="utf-8")
    project = project_fixture([document()])
    assert asyncio.run(sync_documents.sync_documents(project, tmp_path, 30)) == 0
    assert asyncio.run(sync_documents.sync_documents(project, tmp_path, 30)) == 0
    project.documents.upload.assert_awaited_once_with(
        file=tmp_path / "new.md", media_type="text/markdown"
    )
    project.jobs.wait.assert_awaited_once_with(JOB_ID, timeout=30)
    project.documents.delete.assert_not_awaited()
    assert "searchable=True" in capsys.readouterr().out


def test_sync_resumes_existing_pending_job_without_upload(tmp_path):
    (tmp_path / "guide.txt").write_text("existing", encoding="utf-8")
    project = project_fixture([document()])
    pending = SimpleNamespace(
        id=JOB_ID, status="running", stage="embed", progress_percent=50
    )
    project.documents.inspect.side_effect = [
        SimpleNamespace(searchable=False, latest_job=pending),
        SimpleNamespace(searchable=True, latest_job=None),
    ]
    assert asyncio.run(sync_documents.sync_documents(project, tmp_path, 30)) == 0
    project.documents.upload.assert_not_awaited()
    project.jobs.wait.assert_awaited_once_with(JOB_ID, timeout=30)


def test_sync_timeout_keeps_accepted_document_and_reports_incomplete(tmp_path, capsys):
    (tmp_path / "new.txt").write_text("new", encoding="utf-8")
    project = project_fixture()
    project.jobs.wait.side_effect = WaitTimeoutError(
        "job", identifiers={"job_id": JOB_ID}, timeout=1
    )
    project.documents.inspect.return_value = SimpleNamespace(
        searchable=False, latest_job=None
    )
    assert asyncio.run(sync_documents.sync_documents(project, tmp_path, 1)) == 1
    project.documents.delete.assert_not_awaited()
    output = capsys.readouterr()
    assert "not_searchable=1" in output.out
    assert str(JOB_ID) in output.err


def test_listing_visits_all_pages_and_omits_deleted_tombstones():
    seen = []

    def respond(request):
        seen.append(request.url.params.get("after"))
        if len(seen) == 1:
            return httpx.Response(
                200,
                json={"items": [document().to_dict()], "next_cursor": str(DOCUMENT_ID)},
            )
        return httpx.Response(
            200,
            json={
                "items": [
                    document("second.txt", id=UUID(int=5)).to_dict(),
                    document("gone.txt", id=UUID(int=6), state="deleted").to_dict(),
                ],
                "next_cursor": None,
            },
        )

    async def exercise():
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(respond),
        ) as client:
            return await common.list_documents(client.project(PROJECT_ID))

    assert [item.original_filename for item in asyncio.run(exercise())] == [
        "guide.txt",
        "second.txt",
    ]
    assert seen == [None, str(DOCUMENT_ID)]


def test_cleanup_requires_yes_before_deleting():
    project = project_fixture([document()])
    assert asyncio.run(clean_project.clean_project(project, 30, yes=False)) == 2
    project.documents.delete.assert_not_awaited()
    project.deletions.wait.assert_not_awaited()


def test_cleanup_waits_for_receipts_and_verifies_empty_project(capsys):
    project = project_fixture([document(), document("second.txt", id=UUID(int=5))])
    assert asyncio.run(clean_project.clean_project(project, 30, yes=True)) == 0
    assert [call.args[0] for call in project.documents.delete.await_args_list] == [
        DOCUMENT_ID,
        UUID(int=5),
    ]
    assert project.deletions.wait.await_count == 2
    assert "cleaned=2, errors=0, remaining=0" in capsys.readouterr().out


@pytest.mark.parametrize(
    "error",
    [
        WaitTimeoutError("deletion", identifiers={"receipt_id": RECEIPT_ID}, timeout=1),
        OperationFailedError(
            "deletion", "failed", identifiers={"receipt_id": RECEIPT_ID}
        ),
    ],
)
def test_cleanup_does_not_count_accepted_or_failed_deletions_as_cleaned(error, capsys):
    project = project_fixture([document()])
    project.deletions.wait.side_effect = error
    assert asyncio.run(clean_project.clean_project(project, 1, yes=True)) == 1
    output = capsys.readouterr()
    assert "cleaned=0, errors=1, remaining=1" in output.out
    assert str(RECEIPT_ID) in output.err


def test_retrieval_filters_and_full_json_output(tmp_path, capsys):
    args = retrieve.parse_args(
        [
            "purple lanterns",
            "--k",
            "3",
            "--document-id",
            str(DOCUMENT_ID),
            "--tag",
            "guide",
            "--tag",
            "public",
            "--language",
            "en",
        ]
    )
    filters = retrieve.search_filters(args).to_dict()
    assert filters["document_ids"] == [str(DOCUMENT_ID)]
    assert filters["tags_any"] == ["guide", "public"]
    assert filters["language_any"] == ["en"]
    payload = {
        "items": [{"content": "Café", "citation": {"source": "guide"}}],
        "retrieval_id": "example",
    }
    response = SimpleNamespace(items=payload["items"], to_dict=lambda: payload)
    retrieve.output_response(response, None)
    assert json.loads(capsys.readouterr().out) == payload
    output = tmp_path / "results" / "response.json"
    retrieve.output_response(response, output)
    assert json.loads(output.read_text(encoding="utf-8")) == payload
    with pytest.raises(FileExistsError):
        retrieve.output_response(response, output)


@pytest.mark.parametrize(
    "args",
    [
        ["query", "--k", "21"],
        [" "],
        ["query", "--document-id", "not-a-uuid"],
        ["query", "--rerank", "jev"],
    ],
)
def test_retrieval_rejects_invalid_or_unreleased_arguments(args):
    with pytest.raises(SystemExit) as exc:
        retrieve.parse_args(args)
    assert exc.value.code == 2


def test_configuration_loads_only_example_env_and_respects_shell(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "EXAMPLE_DIR", tmp_path)
    for name in (
        "RAGWELL_BASE_URL",
        "RAGWELL_API_KEY",
        "RAGWELL_PROJECT_ID",
        "SYNC_FOLDER",
    ):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / ".env").write_text(
        f"RAGWELL_BASE_URL=https://api.example.test\nRAGWELL_API_KEY=synthetic-file-key\nRAGWELL_PROJECT_ID={PROJECT_ID}\nSYNC_FOLDER=inputs\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("RAGWELL_API_KEY", "synthetic-shell-key")
    settings = common.load_settings()
    assert settings.api_key == "synthetic-shell-key"
    assert settings.sync_folder == tmp_path / "inputs"
    assert settings.project_id == PROJECT_ID
    assert "synthetic-shell-key" not in repr(settings)


@pytest.mark.parametrize(
    "script", ["sync_documents.py", "retrieve.py", "clean_project.py"]
)
def test_cli_help_works_without_credentials(script):
    result = subprocess.run(
        [sys.executable, str(common.EXAMPLE_DIR / script), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "usage:" in result.stdout


def test_retrieve_main_calls_async_sdk_with_selected_params(monkeypatch, capsys):
    args = retrieve.parse_args(["lanterns", "--k", "2"])
    monkeypatch.setattr(retrieve, "parse_args", lambda: args)
    settings = common.Settings(
        "https://api.example.test", "synthetic-key", PROJECT_ID, Path("unused")
    )
    monkeypatch.setattr(retrieve, "load_settings", lambda: settings)
    response = SimpleNamespace(to_dict=lambda: {"items": []})
    project = SimpleNamespace(search=AsyncMock(return_value=response))
    client = AsyncMock()
    client.__aenter__.return_value.project = lambda _: project
    monkeypatch.setattr(retrieve, "AsyncRagwell", lambda **kwargs: client)
    assert asyncio.run(retrieve.main()) == 0
    assert project.search.await_args.kwargs["query"] == "lanterns"
    assert project.search.await_args.kwargs["k"] == 2
    assert "rerank" not in project.search.await_args.kwargs
    assert json.loads(capsys.readouterr().out) == {"items": []}
