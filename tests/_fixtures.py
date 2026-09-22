"""Synthetic machine-contract responses shared by deterministic SDK tests."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import httpx

from ragwell import __version__

PROJECT_ID = "00000000-0000-0000-0000-000000000001"
DOCUMENT_ID = "00000000-0000-0000-0000-000000000002"
VERSION_ID = "00000000-0000-0000-0000-000000000003"
JOB_ID = "00000000-0000-0000-0000-000000000004"
UPLOAD_ID = "00000000-0000-0000-0000-000000000005"
RECEIPT_ID = "00000000-0000-0000-0000-000000000006"
GENERATION_ID = "00000000-0000-0000-0000-000000000007"
SOURCE_ID = "00000000-0000-0000-0000-000000000008"
EXPORT_ID = "00000000-0000-0000-0000-000000000009"
CHUNK_ID = "00000000-0000-0000-0000-00000000000a"
RETRIEVAL_ID = "00000000-0000-0000-0000-00000000000b"
NOW = "2026-09-19T12:00:00+00:00"
LATER = "2026-09-20T12:00:00+00:00"
EXPORT_BYTES = b'{"chunk":"synthetic"}\n'


def metadata() -> dict[str, object]:
    return {"source": None, "author": None, "language": None, "category": None}


def technical_profile() -> dict[str, object]:
    return {
        "extractor": "synthetic",
        "extractor_version": "1",
        "chunker": "synthetic",
        "tokenizer": "synthetic",
        "chunk_max_characters": 1000,
        "chunk_overlap_characters": 100,
        "chunk_max_tokens": None,
        "chunk_overlap_tokens": 10,
        "chunk_min_tokens": 1,
        "representation_version": "rep-v1",
        "boundary_behavior": "bounded",
        "embedding_provider": "synthetic",
        "embedding_model": "synthetic",
        "embedding_dimensions": 3,
        "normalization": "unit",
        "distance_metric": "cosine",
        "retrieval_version": "retrieval-v1",
    }


def project() -> dict[str, object]:
    return {
        "id": PROJECT_ID,
        "name": "Synthetic project",
        "description": None,
        "active_processing_profile": {
            "id": "profile-v1",
            "display_name": "Synthetic",
            "version": "1",
            "embedding_option_id": "embedding-v1",
            "chunking_option_id": "chunking-v1",
            "management": "ragbox_managed",
            "description": "Synthetic profile",
            "extraction_summary": "Synthetic",
            "chunking_summary": "Synthetic",
            "embedding_summary": "Synthetic",
            "retrieval_summary": "Synthetic",
            "technical": technical_profile(),
        },
        "processing_profile_editability": {
            "editable": True,
            "documents_present": False,
            "reason_code": None,
        },
        "created_at": NOW,
        "updated_at": NOW,
    }


def document() -> dict[str, object]:
    return {
        "id": DOCUMENT_ID,
        "original_filename": "guide.txt",
        "state": "ready",
        "tags": ["guide"],
        "metadata": metadata(),
        "metadata_revision": 1,
        "metadata_updated_at": NOW,
        "created_at": NOW,
        "updated_at": NOW,
    }


def upload() -> dict[str, object]:
    return {
        "id": UPLOAD_ID,
        "original_filename": "guide.txt",
        "declared_media_type": "text/plain",
        "declared_size_bytes": 9,
        "declared_sha256": hashlib.sha256(b"synthetic").hexdigest(),
        "tags": [],
        "metadata": metadata(),
        "state": "finalized",
        "expires_at": LATER,
        "created_at": NOW,
        "uploaded_at": NOW,
        "finalized_at": NOW,
        "rejection_code": None,
        "document_id": DOCUMENT_ID,
        "document_version_id": VERSION_ID,
        "job_id": JOB_ID,
        "additive_future_field": "preserved",
    }


def job(status: str = "succeeded") -> dict[str, object]:
    return {
        "id": JOB_ID,
        "document_id": DOCUMENT_ID,
        "document_version_id": VERSION_ID,
        "processing_service_class": {
            "id": "shared-v1",
            "display_name": "Shared",
            "queue_guidance": "Synthetic",
        },
        "status": status,
        "stage": "complete" if status == "succeeded" else "scan",
        "generation": 1,
        "attempt_count": 1,
        "retry_request_count": 0,
        "retryable": status == "failed",
        "progress_percent": 100 if status == "succeeded" else 0,
        "chunk_progress": None,
        "error_code": "synthetic_failure" if status == "failed" else None,
        "error_message": "Synthetic failure" if status == "failed" else None,
        "cancellation_requested_at": None,
        "created_at": NOW,
        "updated_at": NOW,
        "started_at": NOW,
        "finished_at": NOW if status in {"succeeded", "failed", "cancelled"} else None,
    }


def deletion(state: str = "completed") -> dict[str, object]:
    return {
        "id": RECEIPT_ID,
        "document_id": DOCUMENT_ID,
        "state": state,
        "attempt_count": 1,
        "retry_request_count": 0,
        "object_count": 1,
        "deleted_object_count": 1 if state == "completed" else 0,
        "version_count": 1,
        "generation_count": 1,
        "source_count": 1,
        "page_count": 1,
        "chunk_count": 1,
        "vector_count": 1,
        "job_count": 1,
        "attempt_record_count": 1,
        "outbox_count": 1,
        "chunk_part_count": 1,
        "analysis_artifact_count": 0,
        "error_code": "synthetic_failure" if state == "failed" else None,
        "requested_at": NOW,
        "updated_at": NOW,
        "completed_at": NOW if state == "completed" else None,
    }


def export(state: str = "succeeded") -> dict[str, object]:
    return {
        "id": EXPORT_ID,
        "document_version_id": VERSION_ID,
        "generation_id": GENERATION_ID,
        "include_embeddings": False,
        "state": state,
        "chunk_count": 1,
        "completed_parts": 1 if state == "succeeded" else 0,
        "total_parts": 1,
        "total_bytes": len(EXPORT_BYTES),
        "failure_count": 0,
        "error_code": "synthetic_failure" if state == "failed" else None,
        "created_at": NOW,
        "expires_at": LATER,
        "parts": [
            {
                "part_number": 0,
                "byte_size": len(EXPORT_BYTES),
                "sha256": hashlib.sha256(EXPORT_BYTES).hexdigest(),
            }
        ],
    }


def _json_for(method: str, path: str) -> tuple[int, object] | None:
    project_base = f"/v1/projects/{PROJECT_ID}"
    document_base = f"{project_base}/documents/{DOCUMENT_ID}"
    if path == "/v1/document-upload-policy":
        return 200, {
            "formats": [
                {
                    "kind": "plain_text",
                    "display_name": "Text",
                    "media_type": "text/plain",
                    "extensions": [".txt"],
                    "minimum_size_bytes": 1,
                    "maximum_size_bytes": 1000000,
                }
            ],
            "text_page_equivalent_characters": 3000,
            "annotations": {
                "maximum_tags": 20,
                "tag_maximum_characters": 50,
                "tag_maximum_bytes": 100,
                "maximum_total_bytes": 1000,
                "maximum_filter_terms": 20,
                "maximum_document_ids": 20,
                "fields": [],
            },
        }
    if path == project_base:
        return 200, project()
    if path.startswith(f"{project_base}/document-deletions/{RECEIPT_ID}"):
        return 200, deletion()
    if path == f"{project_base}/documents":
        return 200, {"items": [document()], "next_cursor": None}
    if path == document_base:
        return (202, deletion()) if method == "DELETE" else (200, document())
    if path == f"{document_base}/activity":
        return 200, {
            "coverage_started_at": NOW,
            "window_started_at": NOW,
            "measured_at": NOW,
            "returned_searches": 1,
            "chunk_appearances": 1,
            "document_scoped_searches": 1,
            "corpus_searches": 0,
            "last_returned_at": NOW,
            "top_chunks": [],
        }
    if path == f"{document_base}/exports" and method == "POST":
        return 202, export()
    if path == f"{document_base}/exports/{EXPORT_ID}":
        return 200, export()
    if path == f"{document_base}/generations":
        return 200, {"items": [], "next_cursor": None}
    if path == f"{document_base}/generations/{GENERATION_ID}/chunks":
        return 200, {
            "generation_id": GENERATION_ID,
            "items": [],
            "total_count": 0,
            "matching_count": 0,
            "next_cursor": None,
        }
    if path == f"{document_base}/generations/{GENERATION_ID}/sources/{SOURCE_ID}":
        return 200, {
            "generation_id": GENERATION_ID,
            "source_id": SOURCE_ID,
            "coordinate_kind": "text",
            "source_ordinal": 1,
            "page_number": None,
            "character_count": 9,
            "start_offset": 0,
            "end_offset": 9,
            "content": "synthetic",
            "next_offset": None,
            "units": [],
        }
    if path == f"{document_base}/inspection":
        return 200, {
            "document_id": DOCUMENT_ID,
            "measured_at": NOW,
            "searchable": True,
            "active_generation_id": GENERATION_ID,
            "selected_generation": None,
            "source": None,
            "profile": None,
            "latest_job": None,
            "selected_job": None,
            "attempts": [],
            "attempts_truncated": False,
            "deletion_receipt_id": None,
            "job_details_permitted": True,
            "embedding_usage": None,
            "warnings": [],
        }
    if path == f"{document_base}/metadata":
        return 200, document()
    if path == f"{project_base}/embedding-connection":
        return 200, {
            "revision": 1,
            "provider": "synthetic",
            "model": "synthetic",
            "endpoint_url": "https://provider.example.test",
            "funding_source": "system",
            "customer_key_configured": False,
            "system_credentials_available": True,
            "status": "active",
            "health": "ready",
            "health_code": None,
            "validated_at": NOW,
            "updated_at": NOW,
            "notices": [],
        }
    if path == f"{project_base}/jobs":
        return 200, {"items": [job()], "next_cursor": None}
    if path.startswith(f"{project_base}/jobs/{JOB_ID}"):
        return 200, job()
    if path == f"{project_base}/search":
        return 200, {
            "retrieval_id": RETRIEVAL_ID,
            "retrieval_version": "retrieval-v1",
            "profile_id": "profile-v1",
            "items": [],
        }
    if path == f"{project_base}/uploads" and method == "POST":
        return 201, upload()
    if path == f"{project_base}/uploads/{UPLOAD_ID}":
        return 200, upload()
    if path == f"{project_base}/uploads/{UPLOAD_ID}/content":
        return 200, upload()
    if path == f"{project_base}/uploads/{UPLOAD_ID}/finalize":
        return 202, {
            "upload": upload(),
            "document": document(),
            "version": {
                "id": VERSION_ID,
                "document_id": DOCUMENT_ID,
                "version_number": 1,
                "media_type": "text/plain",
                "byte_size": 9,
                "sha256": hashlib.sha256(b"synthetic").hexdigest(),
                "state": "indexed",
                "created_at": NOW,
            },
            "job_id": JOB_ID,
        }
    return None


@dataclass
class RecordingAPI:
    requests: list[httpx.Request] = field(default_factory=list)

    def _respond(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.url.path == "/v1/document-upload-policy":
            assert "Authorization" not in request.headers
        else:
            assert request.headers["Authorization"] == "Bearer test-key"
        assert "Cookie" not in request.headers
        assert "X-CSRF-Token" not in request.headers
        assert request.headers["User-Agent"] == f"ragwell-python/{__version__}"
        path = request.url.path
        if path.endswith(f"/exports/{EXPORT_ID}/parts/0"):
            return httpx.Response(
                200,
                content=EXPORT_BYTES,
                headers={
                    "Content-Type": "application/x-ndjson",
                    "X-Request-ID": "request-synthetic",
                },
            )
        result = _json_for(request.method, path)
        if result is None:
            return httpx.Response(
                404, json={"error": {"code": "not_found", "message": "Not found"}}
            )
        status, payload = result
        return httpx.Response(
            status,
            json=payload,
            headers={"X-Request-ID": "request-synthetic"},
        )

    def sync(self, request: httpx.Request) -> httpx.Response:
        request.read()
        return self._respond(request)

    async def async_(self, request: httpx.Request) -> httpx.Response:
        await request.aread()
        return self._respond(request)
