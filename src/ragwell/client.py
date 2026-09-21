"""Synchronous Ragwell client and local project resource handles."""

from __future__ import annotations

import builtins
import hashlib
import os
from collections.abc import Iterator
from pathlib import Path
from types import TracebackType
from typing import Any, BinaryIO
from uuid import UUID

import httpx

from ._common import (
    SyncFileContent,
    UploadInput,
    as_uuid_list,
    create_temporary_destination,
    finalize_temporary,
    prepare_upload,
    query_params,
    remove_temporary,
    repeated_cursor,
    resolve_configuration,
    resource_id,
)
from ._common import (
    idempotency_key as _make_idempotency_key,
)
from ._deadline import finite_seconds
from ._generated.models import (
    CreateDocumentExportRequest,
    CreateUploadRequest,
    CreateUploadRequestDeclaredMediaType,
    DocumentChunkInfo,
    DocumentChunkPage,
    DocumentDeletionResponse,
    DocumentExportPartResponse,
    DocumentExportResponse,
    DocumentGenerationInfo,
    DocumentGenerationPage,
    DocumentInspectionResponse,
    DocumentListResponse,
    DocumentMetadataInput,
    DocumentResponse,
    DocumentRetrievalActivity,
    DocumentSourcePreview,
    DocumentUploadPolicyResponse,
    EmbeddingConnectionResponse,
    FinalizedIntakeResponse,
    IngestionJobListResponse,
    IngestionJobResponse,
    IngestionJobStatus,
    ProjectResponse,
    ReplaceDocumentMetadataRequest,
    SearchFilters,
    SearchRequest,
    SearchResponse,
    UploadSessionResponse,
)
from ._generated.types import UNSET, Unset
from ._sync_http import DeadlineHTTPTransport
from ._transport import SyncByteStream, SyncTransport
from .errors import (
    DownloadIntegrityError,
    IntegrityMismatch,
    OperationFailedError,
    PaginationError,
    RagwellError,
    WaitTimeoutError,
)
from .types import DownloadResult, UploadCompletion


def _path_id(value: UUID | str, name: str) -> str:
    return str(resource_id(value, name))


def _wait_values(timeout: float, initial_interval: float) -> tuple[float, float]:
    finite_seconds(timeout, "timeout", zero=True)
    finite_seconds(initial_interval, "initial_interval")
    return timeout, initial_interval


class Ragwell:
    """Typed synchronous client for an explicitly selected Ragwell API endpoint."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        operation_timeout: float = 30.0,
        transfer_timeout: float = 300.0,
        verify: bool = True,
        http_client: httpx.Client | None = None,
        owns_http_client: bool = False,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        resolved_url, resolved_key = resolve_configuration(
            base_url=base_url, api_key=api_key
        )
        finite_seconds(operation_timeout, "operation_timeout")
        finite_seconds(transfer_timeout, "transfer_timeout")
        if http_client is not None and transport is not None:
            raise ValueError("transport cannot be combined with http_client")
        if http_client is None:
            http_client = httpx.Client(
                verify=verify,
                follow_redirects=False,
                transport=transport
                if transport is not None
                else DeadlineHTTPTransport(resolved_url, verify=verify),
            )
            owns_http_client = True
        self._transport = SyncTransport(
            base_url=resolved_url,
            api_key=resolved_key,
            client=http_client,
            owns_client=owns_http_client,
            operation_timeout=operation_timeout,
            transfer_timeout=transfer_timeout,
        )
        self.upload_policy = UploadPolicyResource(self._transport)

    def project(self, project_id: UUID | str) -> Project:
        """Create a local project handle without making a network request."""
        return Project(self._transport, resource_id(project_id, "project_id"))

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Ragwell:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Ragwell(base_url={str(self._transport.base_url)!r})"


class UploadPolicyResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def get(self) -> DocumentUploadPolicyResponse:
        return self._transport.request(
            operation_id="get_document_upload_policy_v1_document_upload_policy_get",
            method="GET",
            path="/v1/document-upload-policy",
            model_type=DocumentUploadPolicyResponse,
            expected_statuses={200},
            retry_mode="read",
            authenticated=False,
        )


class Project:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self.id = project_id
        self.embedding_connection = EmbeddingConnectionResource(transport, project_id)
        self.uploads = UploadsResource(transport, project_id)
        self.jobs = JobsResource(transport, project_id)
        self.deletions = DeletionsResource(transport, project_id)
        self.documents = DocumentsResource(transport, project_id, self.jobs)

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self.id}"

    def get(self) -> ProjectResponse:
        return self._transport.request(
            operation_id="get_project_v1_projects__project_id__get",
            method="GET",
            path=self._base_path,
            model_type=ProjectResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    def search(
        self,
        *,
        query: str,
        filters: SearchFilters | None | Unset = UNSET,
        k: int = 5,
    ) -> SearchResponse:
        body = SearchRequest(query=query, filters=filters, k=k)
        return self._transport.request(
            operation_id="search_v1_projects__project_id__search_post",
            method="POST",
            path=f"{self._base_path}/search",
            model_type=SearchResponse,
            expected_statuses={200},
            json=body.to_dict(),
            retry_mode="none",
        )


class EmbeddingConnectionResource:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    def get(self) -> EmbeddingConnectionResponse:
        return self._transport.request(
            operation_id="inspect_embedding_connection_v1_projects__project_id__embedding_connection_get",
            method="GET",
            path=f"/v1/projects/{self._project_id}/embedding-connection",
            model_type=EmbeddingConnectionResponse,
            expected_statuses={200},
            retry_mode="read",
        )


class UploadsResource:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self._project_id}/uploads"

    def create(
        self,
        request: CreateUploadRequest,
        *,
        idempotency_key: str | None = None,
    ) -> UploadSessionResponse:
        key = _make_idempotency_key(idempotency_key)
        return self._transport.request(
            operation_id="create_upload_v1_projects__project_id__uploads_post",
            method="POST",
            path=self._base_path,
            model_type=UploadSessionResponse,
            expected_statuses={201},
            json=request.to_dict(),
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    def get(self, upload_id: UUID | str) -> UploadSessionResponse:
        upload = _path_id(upload_id, "upload_id")
        return self._transport.request(
            operation_id="get_upload_state",
            method="GET",
            path=f"{self._base_path}/{upload}",
            model_type=UploadSessionResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    def upload_content(
        self,
        upload_id: UUID | str,
        *,
        content: bytes | BinaryIO,
        content_type: str,
        content_length: int | None = None,
    ) -> UploadSessionResponse:
        if content_type not in {
            "application/pdf",
            "text/plain",
            "text/markdown",
        }:
            raise ValueError("unsupported upload content_type")
        upload = _path_id(upload_id, "upload_id")
        before_attempt = None
        request_content: bytes | SyncFileContent
        if isinstance(content, bytes):
            length = len(content)
            request_content = content
        else:
            if not content.seekable():
                if content_length is None:
                    raise ValueError(
                        "content_length is required for a non-seekable low-level stream"
                    )
                length = content_length
            else:
                start = content.tell()
                if content_length is None:
                    end = content.seek(0, os.SEEK_END)
                    content.seek(start)
                    length = end - start
                else:
                    length = content_length

                def rewind() -> None:
                    content.seek(start)

                before_attempt = rewind
            request_content = SyncFileContent(content)
        return self._transport.request(
            operation_id="upload_content_v1_projects__project_id__uploads__upload_id__content_put",
            method="PUT",
            path=f"{self._base_path}/{upload}/content",
            model_type=UploadSessionResponse,
            expected_statuses={200},
            headers={"Content-Type": content_type, "Content-Length": str(length)},
            content=request_content,
            retry_mode="replayable"
            if before_attempt is not None or isinstance(content, bytes)
            else "none",
            transfer=True,
            before_attempt=before_attempt,
        )

    def finalize(self, upload_id: UUID | str) -> FinalizedIntakeResponse:
        upload = _path_id(upload_id, "upload_id")
        return self._transport.request(
            operation_id="finalize_upload_v1_projects__project_id__uploads__upload_id__finalize_post",
            method="POST",
            path=f"{self._base_path}/{upload}/finalize",
            model_type=FinalizedIntakeResponse,
            expected_statuses={202},
            retry_mode="replayable",
            transfer=True,
        )


class DocumentsResource:
    def __init__(
        self, transport: SyncTransport, project_id: UUID, jobs: JobsResource
    ) -> None:
        self._transport = transport
        self._project_id = project_id
        self._jobs = jobs
        self.generations = GenerationsResource(transport, project_id)
        self.chunks = ChunksResource(transport, project_id)
        self.sources = SourcesResource(transport, project_id)
        self.exports = ExportsResource(transport, project_id)

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self._project_id}/documents"

    def list(
        self,
        *,
        limit: int = 50,
        document_ids: list[UUID | str] | None = None,
        tags_any: list[str] | None = None,
        tags_all: list[str] | None = None,
        source_any: list[str] | None = None,
        author_any: list[str] | None = None,
        language_any: list[str] | None = None,
        category_any: list[str] | None = None,
        after: UUID | str | None = None,
    ) -> DocumentListResponse:
        cursor = resource_id(after, "after") if after is not None else None
        return self._transport.request(
            operation_id="list_documents_v1_projects__project_id__documents_get",
            method="GET",
            path=self._base_path,
            model_type=DocumentListResponse,
            expected_statuses={200},
            params=query_params(
                limit=limit,
                document_ids=as_uuid_list(document_ids),
                tags_any=tags_any,
                tags_all=tags_all,
                source_any=source_any,
                author_any=author_any,
                language_any=language_any,
                category_any=category_any,
                after=cursor,
            ),
            retry_mode="read",
        )

    def iter(self, **filters: Any) -> Iterator[DocumentResponse]:
        after = filters.pop("after", None)
        seen: set[object] = set()
        while True:
            page = self.list(after=after, **filters)
            next_cursor = page.next_cursor
            if repeated_cursor(next_cursor, seen):
                raise PaginationError("Document pagination repeated a cursor")
            yield from page.items
            after = next_cursor
            if next_cursor is None:
                return

    def get(self, document_id: UUID | str) -> DocumentResponse:
        document = _path_id(document_id, "document_id")
        return self._transport.request(
            operation_id="get_document_v1_projects__project_id__documents__document_id__get",
            method="GET",
            path=f"{self._base_path}/{document}",
            model_type=DocumentResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    def replace_metadata(
        self,
        document_id: UUID | str,
        request: ReplaceDocumentMetadataRequest,
        *,
        idempotency_key: str | None = None,
    ) -> DocumentResponse:
        document = _path_id(document_id, "document_id")
        key = _make_idempotency_key(idempotency_key)
        return self._transport.request(
            operation_id="replace_document_metadata_v1_projects__project_id__documents__document_id__metadata_put",
            method="PUT",
            path=f"{self._base_path}/{document}/metadata",
            model_type=DocumentResponse,
            expected_statuses={200},
            json=request.to_dict(),
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    def delete(
        self,
        document_id: UUID | str,
        *,
        idempotency_key: str | None = None,
    ) -> DocumentDeletionResponse:
        document = _path_id(document_id, "document_id")
        key = _make_idempotency_key(idempotency_key)
        return self._transport.request(
            operation_id="delete_document_v1_projects__project_id__documents__document_id__delete",
            method="DELETE",
            path=f"{self._base_path}/{document}",
            model_type=DocumentDeletionResponse,
            expected_statuses={202},
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    def inspect(
        self,
        document_id: UUID | str,
        *,
        generation_id: UUID | str | None = None,
    ) -> DocumentInspectionResponse:
        document = _path_id(document_id, "document_id")
        generation = (
            resource_id(generation_id, "generation_id")
            if generation_id is not None
            else None
        )
        return self._transport.request(
            operation_id="inspect_document_v1_projects__project_id__documents__document_id__inspection_get",
            method="GET",
            path=f"{self._base_path}/{document}/inspection",
            model_type=DocumentInspectionResponse,
            expected_statuses={200},
            params=query_params(generation_id=generation),
            retry_mode="read",
        )

    def activity(
        self,
        document_id: UUID | str,
        *,
        generation_id: UUID | str | None = None,
    ) -> DocumentRetrievalActivity:
        document = _path_id(document_id, "document_id")
        generation = (
            resource_id(generation_id, "generation_id")
            if generation_id is not None
            else None
        )
        return self._transport.request(
            operation_id="get_document_activity_v1_projects__project_id__documents__document_id__activity_get",
            method="GET",
            path=f"{self._base_path}/{document}/activity",
            model_type=DocumentRetrievalActivity,
            expected_statuses={200},
            params=query_params(generation_id=generation),
            retry_mode="read",
        )

    def upload(
        self,
        *,
        file: UploadInput,
        filename: str | None = None,
        media_type: str | None = None,
        metadata: DocumentMetadataInput | Unset = UNSET,
        tags: builtins.list[str] | Unset = UNSET,
        idempotency_key: str | None = None,
    ) -> FinalizedIntakeResponse:
        with self._transport.scope(
            self._transport.transfer_timeout, "documents.upload"
        ) as budget:
            key = _make_idempotency_key(idempotency_key)
            with prepare_upload(
                file, filename=filename, media_type=media_type, check=budget.check
            ) as prepared:
                request = CreateUploadRequest(
                    original_filename=prepared.filename,
                    declared_media_type=CreateUploadRequestDeclaredMediaType(
                        prepared.media_type
                    ),
                    declared_size_bytes=prepared.size,
                    declared_sha256=prepared.sha256,
                    metadata=metadata,
                    tags=tags,
                )
                try:
                    upload = UploadsResource(self._transport, self._project_id).create(
                        request, idempotency_key=key
                    )
                except RagwellError as exc:
                    raise exc.with_identifiers(
                        project_id=self._project_id, idempotency_key=key
                    ) from None
                try:
                    UploadsResource(self._transport, self._project_id).upload_content(
                        upload.id,
                        content=prepared.stream,
                        content_type=prepared.media_type,
                        content_length=prepared.size,
                    )
                    intake = UploadsResource(
                        self._transport, self._project_id
                    ).finalize(upload.id)
                except RagwellError as exc:
                    raise exc.with_identifiers(
                        project_id=self._project_id,
                        upload_id=upload.id,
                        document_id=upload.document_id,
                        version_id=upload.document_version_id,
                        job_id=upload.job_id,
                        idempotency_key=key,
                    ) from None
            try:
                budget.check()
            except RagwellError as exc:
                raise exc.with_identifiers(
                    project_id=self._project_id,
                    upload_id=intake.upload.id,
                    document_id=intake.document.id,
                    version_id=intake.version.id,
                    job_id=intake.job_id,
                ) from None
            return intake

    def upload_and_wait(
        self,
        *,
        file: UploadInput,
        filename: str | None = None,
        media_type: str | None = None,
        metadata: DocumentMetadataInput | Unset = UNSET,
        tags: builtins.list[str] | Unset = UNSET,
        idempotency_key: str | None = None,
        wait_timeout: float = 300.0,
        initial_interval: float = 1.0,
    ) -> UploadCompletion:
        _wait_values(wait_timeout, initial_interval)
        intake = self.upload(
            file=file,
            filename=filename,
            media_type=media_type,
            metadata=metadata,
            tags=tags,
            idempotency_key=idempotency_key,
        )
        try:
            job = self._jobs.wait(
                intake.job_id,
                timeout=wait_timeout,
                initial_interval=initial_interval,
            )
        except RagwellError as exc:
            exc.with_identifiers(
                project_id=self._project_id,
                upload_id=intake.upload.id,
                document_id=intake.document.id,
                version_id=intake.version.id,
                job_id=intake.job_id,
            )
            raise
        return UploadCompletion(intake=intake, job=job)


class GenerationsResource:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    def list(
        self,
        document_id: UUID | str,
        *,
        after: UUID | str | None = None,
        limit: int = 20,
    ) -> DocumentGenerationPage:
        document = _path_id(document_id, "document_id")
        cursor = resource_id(after, "after") if after is not None else None
        return self._transport.request(
            operation_id="list_document_generations_v1_projects__project_id__documents__document_id__generations_get",
            method="GET",
            path=f"/v1/projects/{self._project_id}/documents/{document}/generations",
            model_type=DocumentGenerationPage,
            expected_statuses={200},
            params=query_params(after=cursor, limit=limit),
            retry_mode="read",
        )

    def iter(
        self,
        document_id: UUID | str,
        *,
        after: UUID | str | None = None,
        limit: int = 20,
    ) -> Iterator[DocumentGenerationInfo]:
        seen: set[object] = set()
        cursor = after
        while True:
            page = self.list(document_id, after=cursor, limit=limit)
            next_cursor = page.next_cursor
            if repeated_cursor(next_cursor, seen):
                raise PaginationError("Generation pagination repeated a cursor")
            yield from page.items
            cursor = next_cursor
            if next_cursor is None:
                return


class ChunksResource:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    def list(
        self,
        document_id: UUID | str,
        generation_id: UUID | str,
        *,
        limit: int = 25,
        after: int | None = None,
        text: str | None = None,
        source_ordinal: int | None = None,
    ) -> DocumentChunkPage:
        document = _path_id(document_id, "document_id")
        generation = _path_id(generation_id, "generation_id")
        return self._transport.request(
            operation_id="list_document_chunks_v1_projects__project_id__documents__document_id__generations__generation_id__chunks_get",
            method="GET",
            path=f"/v1/projects/{self._project_id}/documents/{document}/generations/{generation}/chunks",
            model_type=DocumentChunkPage,
            expected_statuses={200},
            params=query_params(
                limit=limit, after=after, text=text, source_ordinal=source_ordinal
            ),
            retry_mode="read",
        )

    def iter(
        self,
        document_id: UUID | str,
        generation_id: UUID | str,
        **filters: Any,
    ) -> Iterator[DocumentChunkInfo]:
        cursor = filters.pop("after", None)
        seen: set[object] = set()
        while True:
            page = self.list(document_id, generation_id, after=cursor, **filters)
            next_cursor = page.next_cursor
            if repeated_cursor(next_cursor, seen):
                raise PaginationError("Chunk pagination repeated a cursor")
            yield from page.items
            cursor = next_cursor
            if next_cursor is None:
                return


class SourcesResource:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    def get(
        self,
        document_id: UUID | str,
        generation_id: UUID | str,
        source_id: UUID | str,
        *,
        offset: int = 0,
        limit: int = 4000,
    ) -> DocumentSourcePreview:
        document = _path_id(document_id, "document_id")
        generation = _path_id(generation_id, "generation_id")
        source = _path_id(source_id, "source_id")
        return self._transport.request(
            operation_id="inspect_document_source_v1_projects__project_id__documents__document_id__generations__generation_id__sources__source_id__get",
            method="GET",
            path=f"/v1/projects/{self._project_id}/documents/{document}/generations/{generation}/sources/{source}",
            model_type=DocumentSourcePreview,
            expected_statuses={200},
            params=query_params(offset=offset, limit=limit),
            retry_mode="read",
        )


class JobsResource:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self._project_id}/jobs"

    def list(
        self,
        *,
        limit: int = 50,
        document_ids: list[UUID | str] | None = None,
        tags_any: list[str] | None = None,
        tags_all: list[str] | None = None,
        source_any: list[str] | None = None,
        author_any: list[str] | None = None,
        language_any: list[str] | None = None,
        category_any: list[str] | None = None,
        after: str | None = None,
        status: list[IngestionJobStatus] | None = None,
    ) -> IngestionJobListResponse:
        return self._transport.request(
            operation_id="list_jobs_v1_projects__project_id__jobs_get",
            method="GET",
            path=self._base_path,
            model_type=IngestionJobListResponse,
            expected_statuses={200},
            params=query_params(
                limit=limit,
                document_ids=as_uuid_list(document_ids),
                tags_any=tags_any,
                tags_all=tags_all,
                source_any=source_any,
                author_any=author_any,
                language_any=language_any,
                category_any=category_any,
                after=after,
                status=status,
            ),
            retry_mode="read",
        )

    def iter(self, **filters: Any) -> Iterator[IngestionJobResponse]:
        cursor = filters.pop("after", None)
        seen: set[object] = set()
        while True:
            page = self.list(after=cursor, **filters)
            next_cursor = page.next_cursor
            if repeated_cursor(next_cursor, seen):
                raise PaginationError("Job pagination repeated an opaque cursor")
            yield from page.items
            cursor = next_cursor
            if next_cursor is None:
                return

    def get(self, job_id: UUID | str) -> IngestionJobResponse:
        job = _path_id(job_id, "job_id")
        return self._transport.request(
            operation_id="get_job_v1_projects__project_id__jobs__job_id__get",
            method="GET",
            path=f"{self._base_path}/{job}",
            model_type=IngestionJobResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    def retry(
        self, job_id: UUID | str, *, idempotency_key: str | None = None
    ) -> IngestionJobResponse:
        return self._command(job_id, "retry", idempotency_key)

    def cancel(
        self, job_id: UUID | str, *, idempotency_key: str | None = None
    ) -> IngestionJobResponse:
        return self._command(job_id, "cancel", idempotency_key)

    def _command(
        self, job_id: UUID | str, action: str, key_value: str | None
    ) -> IngestionJobResponse:
        job = _path_id(job_id, "job_id")
        key = _make_idempotency_key(key_value)
        operation = (
            "retry_job_v1_projects__project_id__jobs__job_id__retry_post"
            if action == "retry"
            else "cancel_job_v1_projects__project_id__jobs__job_id__cancel_post"
        )
        return self._transport.request(
            operation_id=operation,
            method="POST",
            path=f"{self._base_path}/{job}/{action}",
            model_type=IngestionJobResponse,
            expected_statuses={200},
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    def wait(
        self,
        job_id: UUID | str,
        *,
        timeout: float = 300.0,
        initial_interval: float = 1.0,
    ) -> IngestionJobResponse:
        timeout, interval = _wait_values(timeout, initial_interval)
        job_uuid = resource_id(job_id, "job_id")
        identifiers: dict[str, object] = {
            "project_id": self._project_id,
            "job_id": job_uuid,
        }
        with self._transport.scope(
            timeout,
            "wait",
            error=lambda: WaitTimeoutError(
                "ingestion job", identifiers=identifiers, timeout=timeout
            ),
        ) as budget:
            observing = {"queued", "running", "retry_wait", "cancellation_requested"}
            while True:
                budget.check()
                job = self.get(job_uuid)
                budget.check()
                state = job.status.value
                if state == "succeeded":
                    return job
                if state not in observing:
                    raise OperationFailedError(
                        "ingestion job",
                        state,
                        identifiers={
                            "project_id": self._project_id,
                            "job_id": job_uuid,
                        },
                        error_code=job.error_code,
                        resource_value=job,
                    )
                remaining = budget.remaining()
                self._transport.sleep(min(interval, remaining))
                interval = min(5.0, interval * 1.5)


class DeletionsResource:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self._project_id}/document-deletions"

    def get(self, receipt_id: UUID | str) -> DocumentDeletionResponse:
        receipt = _path_id(receipt_id, "receipt_id")
        return self._transport.request(
            operation_id="get_document_deletion_v1_projects__project_id__document_deletions__receipt_id__get",
            method="GET",
            path=f"{self._base_path}/{receipt}",
            model_type=DocumentDeletionResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    def retry(
        self,
        receipt_id: UUID | str,
        *,
        idempotency_key: str | None = None,
    ) -> DocumentDeletionResponse:
        receipt = _path_id(receipt_id, "receipt_id")
        key = _make_idempotency_key(idempotency_key)
        return self._transport.request(
            operation_id="retry_document_deletion_v1_projects__project_id__document_deletions__receipt_id__retry_post",
            method="POST",
            path=f"{self._base_path}/{receipt}/retry",
            model_type=DocumentDeletionResponse,
            expected_statuses={200},
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    def wait(
        self,
        receipt_id: UUID | str,
        *,
        timeout: float = 300.0,
        initial_interval: float = 1.0,
    ) -> DocumentDeletionResponse:
        timeout, interval = _wait_values(timeout, initial_interval)
        receipt_uuid = resource_id(receipt_id, "receipt_id")
        identifiers: dict[str, object] = {
            "project_id": self._project_id,
            "receipt_id": receipt_uuid,
        }
        with self._transport.scope(
            timeout,
            "wait",
            error=lambda: WaitTimeoutError(
                "document deletion", identifiers=identifiers, timeout=timeout
            ),
        ) as budget:
            while True:
                budget.check()
                receipt = self.get(receipt_uuid)
                budget.check()
                identifiers["document_id"] = receipt.document_id
                state = receipt.state.value
                if state == "completed":
                    return receipt
                if state not in {"pending", "running", "retry_wait"}:
                    raise OperationFailedError(
                        "document deletion",
                        state,
                        identifiers={
                            "project_id": self._project_id,
                            "receipt_id": receipt_uuid,
                            "document_id": receipt.document_id,
                        },
                        error_code=receipt.error_code,
                        resource_value=receipt,
                    )
                remaining = budget.remaining()
                self._transport.sleep(min(interval, remaining))
                interval = min(5.0, interval * 1.5)


class ExportsResource:
    def __init__(self, transport: SyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    def _base_path(self, document_id: UUID | str) -> str:
        document = _path_id(document_id, "document_id")
        return f"/v1/projects/{self._project_id}/documents/{document}/exports"

    def create(
        self,
        document_id: UUID | str,
        request: CreateDocumentExportRequest,
        *,
        idempotency_key: str | None = None,
    ) -> DocumentExportResponse:
        key = _make_idempotency_key(idempotency_key)
        return self._transport.request(
            operation_id="create_document_export_v1_projects__project_id__documents__document_id__exports_post",
            method="POST",
            path=self._base_path(document_id),
            model_type=DocumentExportResponse,
            expected_statuses={202},
            json=request.to_dict(),
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    def get(
        self, document_id: UUID | str, export_id: UUID | str
    ) -> DocumentExportResponse:
        export = _path_id(export_id, "export_id")
        return self._transport.request(
            operation_id="get_document_export_v1_projects__project_id__documents__document_id__exports__export_id__get",
            method="GET",
            path=f"{self._base_path(document_id)}/{export}",
            model_type=DocumentExportResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    def wait(
        self,
        document_id: UUID | str,
        export_id: UUID | str,
        *,
        timeout: float = 300.0,
        initial_interval: float = 1.0,
    ) -> DocumentExportResponse:
        timeout, interval = _wait_values(timeout, initial_interval)
        document_uuid = resource_id(document_id, "document_id")
        export_uuid = resource_id(export_id, "export_id")
        identifiers: dict[str, object] = {
            "project_id": self._project_id,
            "document_id": document_uuid,
            "export_id": export_uuid,
        }
        with self._transport.scope(
            timeout,
            "wait",
            error=lambda: WaitTimeoutError(
                "document export", identifiers=identifiers, timeout=timeout
            ),
        ) as budget:
            while True:
                budget.check()
                export = self.get(document_uuid, export_uuid)
                budget.check()
                state = export.state.value
                if state == "succeeded":
                    return export
                if state not in {"queued", "running"}:
                    raise OperationFailedError(
                        "document export",
                        state,
                        identifiers={
                            "project_id": self._project_id,
                            "document_id": document_uuid,
                            "export_id": export_uuid,
                        },
                        error_code=export.error_code,
                        resource_value=export,
                    )
                remaining = budget.remaining()
                self._transport.sleep(min(interval, remaining))
                interval = min(5.0, interval * 1.5)

    def stream_part(
        self,
        document_id: UUID | str,
        export_id: UUID | str,
        part_number: int,
    ) -> SyncByteStream:
        if not 0 <= part_number <= 199:
            raise ValueError("part_number must be between 0 and 199")
        export = _path_id(export_id, "export_id")
        return self._transport.stream(
            operation_id="download_document_export_part_v1_projects__project_id__documents__document_id__exports__export_id__parts__part_number__get",
            path=f"{self._base_path(document_id)}/{export}/parts/{part_number}",
        )

    def download_part(
        self,
        document_id: UUID | str,
        export_id: UUID | str,
        part: DocumentExportPartResponse,
        destination: str | os.PathLike[str],
        *,
        overwrite: bool = False,
    ) -> DownloadResult:
        with self._transport.scope(
            self._transport.transfer_timeout, "exports.download_part"
        ) as budget:
            destination_path = Path(destination).expanduser()
            output, temporary = create_temporary_destination(
                destination_path, overwrite=overwrite
            )
            digest = hashlib.sha256()
            size = 0
            try:
                with (
                    output,
                    self.stream_part(
                        document_id, export_id, part.part_number
                    ) as stream,
                ):
                    for chunk in stream.iter_bytes():
                        if size + len(chunk) > part.byte_size:
                            raise DownloadIntegrityError(
                                IntegrityMismatch(
                                    expected_size=part.byte_size,
                                    actual_size=size + len(chunk),
                                    expected_sha256=part.sha256,
                                    actual_sha256=digest.hexdigest(),
                                )
                            )
                        output.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                    budget.check()
                    output.flush()
                    os.fsync(output.fileno())
                budget.check()
                actual_sha = digest.hexdigest()
                if size != part.byte_size or actual_sha != part.sha256:
                    raise DownloadIntegrityError(
                        IntegrityMismatch(
                            expected_size=part.byte_size,
                            actual_size=size,
                            expected_sha256=part.sha256,
                            actual_sha256=actual_sha,
                        )
                    )
                finalize_temporary(temporary, destination_path, overwrite=overwrite)
            except BaseException:
                remove_temporary(temporary)
                raise
            budget.check()
            return DownloadResult(path=destination_path, part=part)


__all__ = ["Project", "Ragwell"]
