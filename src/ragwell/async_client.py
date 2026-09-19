"""Asynchronous Ragwell client with capability parity with the sync client."""

from __future__ import annotations

import asyncio
import builtins
import hashlib
import os
from collections.abc import AsyncIterator
from pathlib import Path
from types import TracebackType
from typing import Any, BinaryIO
from uuid import UUID

import httpx

from ._common import (
    AsyncFileContent,
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
from ._transport import AsyncByteStream, AsyncTransport
from .errors import (
    ApiError,
    DownloadIntegrityError,
    IntegrityMismatch,
    OperationFailedError,
    PaginationError,
    ProtocolError,
    TransportError,
    WaitTimeoutError,
)
from .types import DownloadResult, UploadCompletion


def _path_id(value: UUID | str, name: str) -> str:
    return str(resource_id(value, name))


def _wait_values(timeout: float, initial_interval: float) -> tuple[float, float]:
    if timeout < 0:
        raise ValueError("timeout must be non-negative")
    if initial_interval <= 0:
        raise ValueError("initial_interval must be positive")
    return timeout, initial_interval


class AsyncRagwell:
    """Typed asynchronous client for an explicitly selected Ragwell endpoint."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        operation_timeout: float = 30.0,
        transfer_timeout: float = 300.0,
        verify: bool = True,
        http_client: httpx.AsyncClient | None = None,
        owns_http_client: bool = False,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        resolved_url, resolved_key = resolve_configuration(
            base_url=base_url, api_key=api_key
        )
        if operation_timeout <= 0 or transfer_timeout <= 0:
            raise ValueError("operation and transfer timeouts must be positive")
        if http_client is not None and transport is not None:
            raise ValueError("transport cannot be combined with http_client")
        if http_client is None:
            http_client = httpx.AsyncClient(
                verify=verify,
                follow_redirects=False,
                transport=transport,
            )
            owns_http_client = True
        self._transport = AsyncTransport(
            base_url=resolved_url,
            api_key=resolved_key,
            client=http_client,
            owns_client=owns_http_client,
            operation_timeout=operation_timeout,
            transfer_timeout=transfer_timeout,
        )
        self.upload_policy = AsyncUploadPolicyResource(self._transport)

    def project(self, project_id: UUID | str) -> AsyncProject:
        """Create a local project handle without making a network request."""
        return AsyncProject(self._transport, resource_id(project_id, "project_id"))

    async def aclose(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> AsyncRagwell:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"AsyncRagwell(base_url={str(self._transport.base_url)!r})"


class AsyncUploadPolicyResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def get(self) -> DocumentUploadPolicyResponse:
        return await self._transport.request(
            operation_id="get_document_upload_policy_v1_document_upload_policy_get",
            method="GET",
            path="/v1/document-upload-policy",
            model_type=DocumentUploadPolicyResponse,
            expected_statuses={200},
            retry_mode="read",
            authenticated=False,
        )


class AsyncProject:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self.id = project_id
        self.embedding_connection = AsyncEmbeddingConnectionResource(
            transport, project_id
        )
        self.uploads = AsyncUploadsResource(transport, project_id)
        self.jobs = AsyncJobsResource(transport, project_id)
        self.deletions = AsyncDeletionsResource(transport, project_id)
        self.documents = AsyncDocumentsResource(transport, project_id, self.jobs)

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self.id}"

    async def get(self) -> ProjectResponse:
        return await self._transport.request(
            operation_id="get_project_v1_projects__project_id__get",
            method="GET",
            path=self._base_path,
            model_type=ProjectResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    async def search(
        self,
        *,
        query: str,
        filters: SearchFilters | None | Unset = UNSET,
        k: int = 5,
    ) -> SearchResponse:
        body = SearchRequest(query=query, filters=filters, k=k)
        return await self._transport.request(
            operation_id="search_v1_projects__project_id__search_post",
            method="POST",
            path=f"{self._base_path}/search",
            model_type=SearchResponse,
            expected_statuses={200},
            json=body.to_dict(),
            retry_mode="none",
        )


class AsyncEmbeddingConnectionResource:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    async def get(self) -> EmbeddingConnectionResponse:
        return await self._transport.request(
            operation_id="inspect_embedding_connection_v1_projects__project_id__embedding_connection_get",
            method="GET",
            path=f"/v1/projects/{self._project_id}/embedding-connection",
            model_type=EmbeddingConnectionResponse,
            expected_statuses={200},
            retry_mode="read",
        )


class AsyncUploadsResource:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self._project_id}/uploads"

    async def create(
        self,
        request: CreateUploadRequest,
        *,
        idempotency_key: str | None = None,
    ) -> UploadSessionResponse:
        key = _make_idempotency_key(idempotency_key)
        return await self._transport.request(
            operation_id="create_upload_v1_projects__project_id__uploads_post",
            method="POST",
            path=self._base_path,
            model_type=UploadSessionResponse,
            expected_statuses={201},
            json=request.to_dict(),
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    async def get(self, upload_id: UUID | str) -> UploadSessionResponse:
        upload = _path_id(upload_id, "upload_id")
        return await self._transport.request(
            operation_id="get_upload_state",
            method="GET",
            path=f"{self._base_path}/{upload}",
            model_type=UploadSessionResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    async def upload_content(
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
        request_content: bytes | AsyncFileContent
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
                    end = await asyncio.to_thread(content.seek, 0, os.SEEK_END)
                    await asyncio.to_thread(content.seek, start)
                    length = end - start
                else:
                    length = content_length

                def rewind() -> None:
                    content.seek(start)

                before_attempt = rewind
            request_content = AsyncFileContent(content)
        return await self._transport.request(
            operation_id="upload_content_v1_projects__project_id__uploads__upload_id__content_put",
            method="PUT",
            path=f"{self._base_path}/{upload}/content",
            model_type=UploadSessionResponse,
            expected_statuses={200},
            headers={"Content-Type": content_type, "Content-Length": str(length)},
            content=request_content,
            retry_mode=(
                "replayable"
                if isinstance(content, bytes) or before_attempt is not None
                else "none"
            ),
            transfer=True,
            before_attempt=before_attempt,
        )

    async def finalize(self, upload_id: UUID | str) -> FinalizedIntakeResponse:
        upload = _path_id(upload_id, "upload_id")
        return await self._transport.request(
            operation_id="finalize_upload_v1_projects__project_id__uploads__upload_id__finalize_post",
            method="POST",
            path=f"{self._base_path}/{upload}/finalize",
            model_type=FinalizedIntakeResponse,
            expected_statuses={202},
            retry_mode="replayable",
            transfer=True,
        )


class AsyncDocumentsResource:
    def __init__(
        self, transport: AsyncTransport, project_id: UUID, jobs: AsyncJobsResource
    ) -> None:
        self._transport = transport
        self._project_id = project_id
        self._jobs = jobs
        self.generations = AsyncGenerationsResource(transport, project_id)
        self.chunks = AsyncChunksResource(transport, project_id)
        self.sources = AsyncSourcesResource(transport, project_id)
        self.exports = AsyncExportsResource(transport, project_id)

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self._project_id}/documents"

    async def list(
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
        return await self._transport.request(
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

    async def iter(self, **filters: Any) -> AsyncIterator[DocumentResponse]:
        cursor = filters.pop("after", None)
        seen: set[object] = set()
        while True:
            page = await self.list(after=cursor, **filters)
            next_cursor = page.next_cursor
            if repeated_cursor(next_cursor, seen):
                raise PaginationError("Document pagination repeated a cursor")
            for item in page.items:
                yield item
            cursor = next_cursor
            if next_cursor is None:
                return

    async def get(self, document_id: UUID | str) -> DocumentResponse:
        document = _path_id(document_id, "document_id")
        return await self._transport.request(
            operation_id="get_document_v1_projects__project_id__documents__document_id__get",
            method="GET",
            path=f"{self._base_path}/{document}",
            model_type=DocumentResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    async def replace_metadata(
        self,
        document_id: UUID | str,
        request: ReplaceDocumentMetadataRequest,
        *,
        idempotency_key: str | None = None,
    ) -> DocumentResponse:
        document = _path_id(document_id, "document_id")
        key = _make_idempotency_key(idempotency_key)
        return await self._transport.request(
            operation_id="replace_document_metadata_v1_projects__project_id__documents__document_id__metadata_put",
            method="PUT",
            path=f"{self._base_path}/{document}/metadata",
            model_type=DocumentResponse,
            expected_statuses={200},
            json=request.to_dict(),
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    async def delete(
        self,
        document_id: UUID | str,
        *,
        idempotency_key: str | None = None,
    ) -> DocumentDeletionResponse:
        document = _path_id(document_id, "document_id")
        key = _make_idempotency_key(idempotency_key)
        return await self._transport.request(
            operation_id="delete_document_v1_projects__project_id__documents__document_id__delete",
            method="DELETE",
            path=f"{self._base_path}/{document}",
            model_type=DocumentDeletionResponse,
            expected_statuses={202},
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    async def inspect(
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
        return await self._transport.request(
            operation_id="inspect_document_v1_projects__project_id__documents__document_id__inspection_get",
            method="GET",
            path=f"{self._base_path}/{document}/inspection",
            model_type=DocumentInspectionResponse,
            expected_statuses={200},
            params=query_params(generation_id=generation),
            retry_mode="read",
        )

    async def activity(
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
        return await self._transport.request(
            operation_id="get_document_activity_v1_projects__project_id__documents__document_id__activity_get",
            method="GET",
            path=f"{self._base_path}/{document}/activity",
            model_type=DocumentRetrievalActivity,
            expected_statuses={200},
            params=query_params(generation_id=generation),
            retry_mode="read",
        )

    async def upload(
        self,
        *,
        file: UploadInput,
        filename: str | None = None,
        media_type: str | None = None,
        metadata: DocumentMetadataInput | Unset = UNSET,
        tags: builtins.list[str] | Unset = UNSET,
        idempotency_key: str | None = None,
    ) -> FinalizedIntakeResponse:
        key = _make_idempotency_key(idempotency_key)
        prepared = await asyncio.to_thread(
            prepare_upload,
            file,
            filename=filename,
            media_type=media_type,
        )
        uploads = AsyncUploadsResource(self._transport, self._project_id)
        try:
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
                upload = await uploads.create(request, idempotency_key=key)
            except (ApiError, TransportError, ProtocolError) as exc:
                raise exc.with_identifiers(
                    project_id=self._project_id, idempotency_key=key
                ) from None
            try:
                await uploads.upload_content(
                    upload.id,
                    content=prepared.stream,
                    content_type=prepared.media_type,
                    content_length=prepared.size,
                )
                return await uploads.finalize(upload.id)
            except (ApiError, TransportError, ProtocolError) as exc:
                raise exc.with_identifiers(
                    project_id=self._project_id, upload_id=upload.id
                ) from None
        finally:
            await asyncio.to_thread(prepared.close)

    async def upload_and_wait(
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
        intake = await self.upload(
            file=file,
            filename=filename,
            media_type=media_type,
            metadata=metadata,
            tags=tags,
            idempotency_key=idempotency_key,
        )
        try:
            job = await self._jobs.wait(
                intake.job_id,
                timeout=wait_timeout,
                initial_interval=initial_interval,
            )
        except WaitTimeoutError as exc:
            exc.identifiers.update(
                {
                    "document_id": str(intake.document.id),
                    "upload_id": str(intake.upload.id),
                }
            )
            raise
        return UploadCompletion(intake=intake, job=job)


class AsyncGenerationsResource:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    async def list(
        self,
        document_id: UUID | str,
        *,
        after: UUID | str | None = None,
        limit: int = 20,
    ) -> DocumentGenerationPage:
        document = _path_id(document_id, "document_id")
        cursor = resource_id(after, "after") if after is not None else None
        return await self._transport.request(
            operation_id="list_document_generations_v1_projects__project_id__documents__document_id__generations_get",
            method="GET",
            path=f"/v1/projects/{self._project_id}/documents/{document}/generations",
            model_type=DocumentGenerationPage,
            expected_statuses={200},
            params=query_params(after=cursor, limit=limit),
            retry_mode="read",
        )

    async def iter(
        self,
        document_id: UUID | str,
        *,
        after: UUID | str | None = None,
        limit: int = 20,
    ) -> AsyncIterator[DocumentGenerationInfo]:
        seen: set[object] = set()
        cursor = after
        while True:
            page = await self.list(document_id, after=cursor, limit=limit)
            next_cursor = page.next_cursor
            if repeated_cursor(next_cursor, seen):
                raise PaginationError("Generation pagination repeated a cursor")
            for item in page.items:
                yield item
            cursor = next_cursor
            if next_cursor is None:
                return


class AsyncChunksResource:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    async def list(
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
        return await self._transport.request(
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

    async def iter(
        self,
        document_id: UUID | str,
        generation_id: UUID | str,
        **filters: Any,
    ) -> AsyncIterator[DocumentChunkInfo]:
        cursor = filters.pop("after", None)
        seen: set[object] = set()
        while True:
            page = await self.list(document_id, generation_id, after=cursor, **filters)
            next_cursor = page.next_cursor
            if repeated_cursor(next_cursor, seen):
                raise PaginationError("Chunk pagination repeated a cursor")
            for item in page.items:
                yield item
            cursor = next_cursor
            if next_cursor is None:
                return


class AsyncSourcesResource:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    async def get(
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
        return await self._transport.request(
            operation_id="inspect_document_source_v1_projects__project_id__documents__document_id__generations__generation_id__sources__source_id__get",
            method="GET",
            path=f"/v1/projects/{self._project_id}/documents/{document}/generations/{generation}/sources/{source}",
            model_type=DocumentSourcePreview,
            expected_statuses={200},
            params=query_params(offset=offset, limit=limit),
            retry_mode="read",
        )


class AsyncJobsResource:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self._project_id}/jobs"

    async def list(
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
        return await self._transport.request(
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

    async def iter(self, **filters: Any) -> AsyncIterator[IngestionJobResponse]:
        cursor = filters.pop("after", None)
        seen: set[object] = set()
        while True:
            page = await self.list(after=cursor, **filters)
            next_cursor = page.next_cursor
            if repeated_cursor(next_cursor, seen):
                raise PaginationError("Job pagination repeated an opaque cursor")
            for item in page.items:
                yield item
            cursor = next_cursor
            if next_cursor is None:
                return

    async def get(self, job_id: UUID | str) -> IngestionJobResponse:
        job = _path_id(job_id, "job_id")
        return await self._transport.request(
            operation_id="get_job_v1_projects__project_id__jobs__job_id__get",
            method="GET",
            path=f"{self._base_path}/{job}",
            model_type=IngestionJobResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    async def retry(
        self, job_id: UUID | str, *, idempotency_key: str | None = None
    ) -> IngestionJobResponse:
        return await self._command(job_id, "retry", idempotency_key)

    async def cancel(
        self, job_id: UUID | str, *, idempotency_key: str | None = None
    ) -> IngestionJobResponse:
        return await self._command(job_id, "cancel", idempotency_key)

    async def _command(
        self, job_id: UUID | str, action: str, key_value: str | None
    ) -> IngestionJobResponse:
        job = _path_id(job_id, "job_id")
        key = _make_idempotency_key(key_value)
        operation = (
            "retry_job_v1_projects__project_id__jobs__job_id__retry_post"
            if action == "retry"
            else "cancel_job_v1_projects__project_id__jobs__job_id__cancel_post"
        )
        return await self._transport.request(
            operation_id=operation,
            method="POST",
            path=f"{self._base_path}/{job}/{action}",
            model_type=IngestionJobResponse,
            expected_statuses={200},
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    async def wait(
        self,
        job_id: UUID | str,
        *,
        timeout: float = 300.0,
        initial_interval: float = 1.0,
    ) -> IngestionJobResponse:
        timeout, interval = _wait_values(timeout, initial_interval)
        job_uuid = resource_id(job_id, "job_id")
        deadline = self._transport.monotonic() + timeout
        observing = {"queued", "running", "retry_wait", "cancellation_requested"}
        while True:
            job = await self.get(job_uuid)
            state = job.status.value
            if state == "succeeded":
                return job
            if state not in observing:
                raise OperationFailedError(
                    "ingestion job",
                    state,
                    identifiers={"project_id": self._project_id, "job_id": job_uuid},
                    error_code=job.error_code,
                    resource_value=job,
                )
            remaining = deadline - self._transport.monotonic()
            if remaining <= 0:
                raise WaitTimeoutError(
                    "ingestion job",
                    identifiers={"project_id": self._project_id, "job_id": job_uuid},
                    timeout=timeout,
                )
            await self._transport.sleep(min(interval, remaining))
            interval = min(5.0, interval * 1.5)


class AsyncDeletionsResource:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    @property
    def _base_path(self) -> str:
        return f"/v1/projects/{self._project_id}/document-deletions"

    async def get(self, receipt_id: UUID | str) -> DocumentDeletionResponse:
        receipt = _path_id(receipt_id, "receipt_id")
        return await self._transport.request(
            operation_id="get_document_deletion_v1_projects__project_id__document_deletions__receipt_id__get",
            method="GET",
            path=f"{self._base_path}/{receipt}",
            model_type=DocumentDeletionResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    async def retry(
        self,
        receipt_id: UUID | str,
        *,
        idempotency_key: str | None = None,
    ) -> DocumentDeletionResponse:
        receipt = _path_id(receipt_id, "receipt_id")
        key = _make_idempotency_key(idempotency_key)
        return await self._transport.request(
            operation_id="retry_document_deletion_v1_projects__project_id__document_deletions__receipt_id__retry_post",
            method="POST",
            path=f"{self._base_path}/{receipt}/retry",
            model_type=DocumentDeletionResponse,
            expected_statuses={200},
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    async def wait(
        self,
        receipt_id: UUID | str,
        *,
        timeout: float = 300.0,
        initial_interval: float = 1.0,
    ) -> DocumentDeletionResponse:
        timeout, interval = _wait_values(timeout, initial_interval)
        receipt_uuid = resource_id(receipt_id, "receipt_id")
        deadline = self._transport.monotonic() + timeout
        while True:
            receipt = await self.get(receipt_uuid)
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
            remaining = deadline - self._transport.monotonic()
            if remaining <= 0:
                raise WaitTimeoutError(
                    "document deletion",
                    identifiers={
                        "project_id": self._project_id,
                        "receipt_id": receipt_uuid,
                        "document_id": receipt.document_id,
                    },
                    timeout=timeout,
                )
            await self._transport.sleep(min(interval, remaining))
            interval = min(5.0, interval * 1.5)


class AsyncExportsResource:
    def __init__(self, transport: AsyncTransport, project_id: UUID) -> None:
        self._transport = transport
        self._project_id = project_id

    def _base_path(self, document_id: UUID | str) -> str:
        document = _path_id(document_id, "document_id")
        return f"/v1/projects/{self._project_id}/documents/{document}/exports"

    async def create(
        self,
        document_id: UUID | str,
        request: CreateDocumentExportRequest,
        *,
        idempotency_key: str | None = None,
    ) -> DocumentExportResponse:
        key = _make_idempotency_key(idempotency_key)
        return await self._transport.request(
            operation_id="create_document_export_v1_projects__project_id__documents__document_id__exports_post",
            method="POST",
            path=self._base_path(document_id),
            model_type=DocumentExportResponse,
            expected_statuses={202},
            json=request.to_dict(),
            headers={"Idempotency-Key": key},
            retry_mode="replayable",
        )

    async def get(
        self, document_id: UUID | str, export_id: UUID | str
    ) -> DocumentExportResponse:
        export = _path_id(export_id, "export_id")
        return await self._transport.request(
            operation_id="get_document_export_v1_projects__project_id__documents__document_id__exports__export_id__get",
            method="GET",
            path=f"{self._base_path(document_id)}/{export}",
            model_type=DocumentExportResponse,
            expected_statuses={200},
            retry_mode="read",
        )

    async def wait(
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
        deadline = self._transport.monotonic() + timeout
        while True:
            export = await self.get(document_uuid, export_uuid)
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
            remaining = deadline - self._transport.monotonic()
            if remaining <= 0:
                raise WaitTimeoutError(
                    "document export",
                    identifiers={
                        "project_id": self._project_id,
                        "document_id": document_uuid,
                        "export_id": export_uuid,
                    },
                    timeout=timeout,
                )
            await self._transport.sleep(min(interval, remaining))
            interval = min(5.0, interval * 1.5)

    async def stream_part(
        self,
        document_id: UUID | str,
        export_id: UUID | str,
        part_number: int,
    ) -> AsyncByteStream:
        if not 0 <= part_number <= 199:
            raise ValueError("part_number must be between 0 and 199")
        export = _path_id(export_id, "export_id")
        return await self._transport.stream(
            operation_id="download_document_export_part_v1_projects__project_id__documents__document_id__exports__export_id__parts__part_number__get",
            path=f"{self._base_path(document_id)}/{export}/parts/{part_number}",
        )

    async def download_part(
        self,
        document_id: UUID | str,
        export_id: UUID | str,
        part: DocumentExportPartResponse,
        destination: str | os.PathLike[str],
        *,
        overwrite: bool = False,
    ) -> DownloadResult:
        destination_path = Path(destination).expanduser()
        output, temporary = await asyncio.to_thread(
            create_temporary_destination, destination_path, overwrite=overwrite
        )
        digest = hashlib.sha256()
        size = 0
        try:
            stream = await self.stream_part(document_id, export_id, part.part_number)
            try:
                async for chunk in stream.iter_bytes():
                    await asyncio.to_thread(output.write, chunk)
                    digest.update(chunk)
                    size += len(chunk)
                await asyncio.to_thread(output.flush)
                await asyncio.to_thread(os.fsync, output.fileno())
            finally:
                await stream.aclose()
                await asyncio.to_thread(output.close)
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
            await asyncio.to_thread(
                finalize_temporary, temporary, destination_path, overwrite=overwrite
            )
        except BaseException:
            if not output.closed:
                await asyncio.to_thread(output.close)
            await asyncio.to_thread(remove_temporary, temporary)
            raise
        return DownloadResult(path=destination_path, part=part)


__all__ = ["AsyncProject", "AsyncRagwell"]
