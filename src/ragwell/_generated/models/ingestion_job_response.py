from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ingestion_job_status import IngestionJobStatus
from ..models.ingestion_stage import IngestionStage
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chunk_stage_progress import ChunkStageProgress
    from ..models.command_acceptance import CommandAcceptance
    from ..models.processing_service_class_response import (
        ProcessingServiceClassResponse,
    )


T = TypeVar("T", bound="IngestionJobResponse")


@_attrs_define
class IngestionJobResponse:
    attempt_count: int
    cancellation_requested_at: datetime.datetime | None
    chunk_progress: ChunkStageProgress | None
    created_at: datetime.datetime
    document_id: UUID
    document_version_id: UUID
    error_code: None | str
    error_message: None | str
    finished_at: datetime.datetime | None
    generation: int
    id: UUID
    processing_service_class: ProcessingServiceClassResponse
    progress_percent: int
    retry_request_count: int
    retryable: bool
    stage: IngestionStage
    started_at: datetime.datetime | None
    status: IngestionJobStatus
    updated_at: datetime.datetime
    command: CommandAcceptance | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.chunk_stage_progress import ChunkStageProgress
        from ..models.command_acceptance import CommandAcceptance

        attempt_count = self.attempt_count

        cancellation_requested_at: None | str
        if isinstance(self.cancellation_requested_at, datetime.datetime):
            cancellation_requested_at = self.cancellation_requested_at.isoformat()
        else:
            cancellation_requested_at = self.cancellation_requested_at

        chunk_progress: dict[str, Any] | None
        if isinstance(self.chunk_progress, ChunkStageProgress):
            chunk_progress = self.chunk_progress.to_dict()
        else:
            chunk_progress = self.chunk_progress

        created_at = self.created_at.isoformat()

        document_id = str(self.document_id)

        document_version_id = str(self.document_version_id)

        error_code: None | str
        error_code = self.error_code

        error_message: None | str
        error_message = self.error_message

        finished_at: None | str
        if isinstance(self.finished_at, datetime.datetime):
            finished_at = self.finished_at.isoformat()
        else:
            finished_at = self.finished_at

        generation = self.generation

        id = str(self.id)

        processing_service_class = self.processing_service_class.to_dict()

        progress_percent = self.progress_percent

        retry_request_count = self.retry_request_count

        retryable = self.retryable

        stage = self.stage.value

        started_at: None | str
        if isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        status = self.status.value

        updated_at = self.updated_at.isoformat()

        command: dict[str, Any] | None | Unset
        if isinstance(self.command, Unset):
            command = UNSET
        elif isinstance(self.command, CommandAcceptance):
            command = self.command.to_dict()
        else:
            command = self.command

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attempt_count": attempt_count,
                "cancellation_requested_at": cancellation_requested_at,
                "chunk_progress": chunk_progress,
                "created_at": created_at,
                "document_id": document_id,
                "document_version_id": document_version_id,
                "error_code": error_code,
                "error_message": error_message,
                "finished_at": finished_at,
                "generation": generation,
                "id": id,
                "processing_service_class": processing_service_class,
                "progress_percent": progress_percent,
                "retry_request_count": retry_request_count,
                "retryable": retryable,
                "stage": stage,
                "started_at": started_at,
                "status": status,
                "updated_at": updated_at,
            }
        )
        if command is not UNSET:
            field_dict["command"] = command

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chunk_stage_progress import ChunkStageProgress
        from ..models.command_acceptance import CommandAcceptance
        from ..models.processing_service_class_response import (
            ProcessingServiceClassResponse,
        )

        d = dict(src_dict)
        attempt_count = d.pop("attempt_count")

        def _parse_cancellation_requested_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                cancellation_requested_at_type_0 = datetime.datetime.fromisoformat(data)

                return cancellation_requested_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        cancellation_requested_at = _parse_cancellation_requested_at(
            d.pop("cancellation_requested_at")
        )

        def _parse_chunk_progress(data: object) -> ChunkStageProgress | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                chunk_progress_type_0 = ChunkStageProgress.from_dict(data)

                return chunk_progress_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChunkStageProgress | None, data)

        chunk_progress = _parse_chunk_progress(d.pop("chunk_progress"))

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        document_id = UUID(d.pop("document_id"))

        document_version_id = UUID(d.pop("document_version_id"))

        def _parse_error_code(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error_code = _parse_error_code(d.pop("error_code"))

        def _parse_error_message(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error_message = _parse_error_message(d.pop("error_message"))

        def _parse_finished_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                finished_at_type_0 = datetime.datetime.fromisoformat(data)

                return finished_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        finished_at = _parse_finished_at(d.pop("finished_at"))

        generation = d.pop("generation")

        id = UUID(d.pop("id"))

        processing_service_class = ProcessingServiceClassResponse.from_dict(
            d.pop("processing_service_class")
        )

        progress_percent = d.pop("progress_percent")

        retry_request_count = d.pop("retry_request_count")

        retryable = d.pop("retryable")

        stage = IngestionStage(d.pop("stage"))

        def _parse_started_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = datetime.datetime.fromisoformat(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        started_at = _parse_started_at(d.pop("started_at"))

        status = IngestionJobStatus(d.pop("status"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        def _parse_command(data: object) -> CommandAcceptance | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                command_type_0 = CommandAcceptance.from_dict(data)

                return command_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CommandAcceptance | None | Unset, data)

        command = _parse_command(d.pop("command", UNSET))

        ingestion_job_response = cls(
            attempt_count=attempt_count,
            cancellation_requested_at=cancellation_requested_at,
            chunk_progress=chunk_progress,
            created_at=created_at,
            document_id=document_id,
            document_version_id=document_version_id,
            error_code=error_code,
            error_message=error_message,
            finished_at=finished_at,
            generation=generation,
            id=id,
            processing_service_class=processing_service_class,
            progress_percent=progress_percent,
            retry_request_count=retry_request_count,
            retryable=retryable,
            stage=stage,
            started_at=started_at,
            status=status,
            updated_at=updated_at,
            command=command,
        )

        ingestion_job_response.additional_properties = d
        return ingestion_job_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
