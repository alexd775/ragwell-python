from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ingestion_job_status import IngestionJobStatus
from ..models.ingestion_stage import IngestionStage

if TYPE_CHECKING:
    from ..models.chunk_stage_progress import ChunkStageProgress


T = TypeVar("T", bound="DocumentJobInfo")


@_attrs_define
class DocumentJobInfo:
    attempt_count: int
    can_cancel: bool
    can_retry: bool
    chunk_progress: ChunkStageProgress | None
    created_at: datetime.datetime
    document_version_id: UUID
    error_code: None | str
    error_message: None | str
    finished_at: datetime.datetime | None
    generation: int
    id: UUID
    profile_id: str
    progress_percent: int
    retry_not_before: datetime.datetime | None
    retry_request_count: int
    stage: IngestionStage
    started_at: datetime.datetime | None
    status: IngestionJobStatus
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.chunk_stage_progress import ChunkStageProgress

        attempt_count = self.attempt_count

        can_cancel = self.can_cancel

        can_retry = self.can_retry

        chunk_progress: dict[str, Any] | None
        if isinstance(self.chunk_progress, ChunkStageProgress):
            chunk_progress = self.chunk_progress.to_dict()
        else:
            chunk_progress = self.chunk_progress

        created_at = self.created_at.isoformat()

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

        profile_id = self.profile_id

        progress_percent = self.progress_percent

        retry_not_before: None | str
        if isinstance(self.retry_not_before, datetime.datetime):
            retry_not_before = self.retry_not_before.isoformat()
        else:
            retry_not_before = self.retry_not_before

        retry_request_count = self.retry_request_count

        stage = self.stage.value

        started_at: None | str
        if isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        status = self.status.value

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attempt_count": attempt_count,
                "can_cancel": can_cancel,
                "can_retry": can_retry,
                "chunk_progress": chunk_progress,
                "created_at": created_at,
                "document_version_id": document_version_id,
                "error_code": error_code,
                "error_message": error_message,
                "finished_at": finished_at,
                "generation": generation,
                "id": id,
                "profile_id": profile_id,
                "progress_percent": progress_percent,
                "retry_not_before": retry_not_before,
                "retry_request_count": retry_request_count,
                "stage": stage,
                "started_at": started_at,
                "status": status,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chunk_stage_progress import ChunkStageProgress

        d = dict(src_dict)
        attempt_count = d.pop("attempt_count")

        can_cancel = d.pop("can_cancel")

        can_retry = d.pop("can_retry")

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

        profile_id = d.pop("profile_id")

        progress_percent = d.pop("progress_percent")

        def _parse_retry_not_before(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                retry_not_before_type_0 = datetime.datetime.fromisoformat(data)

                return retry_not_before_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        retry_not_before = _parse_retry_not_before(d.pop("retry_not_before"))

        retry_request_count = d.pop("retry_request_count")

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

        document_job_info = cls(
            attempt_count=attempt_count,
            can_cancel=can_cancel,
            can_retry=can_retry,
            chunk_progress=chunk_progress,
            created_at=created_at,
            document_version_id=document_version_id,
            error_code=error_code,
            error_message=error_message,
            finished_at=finished_at,
            generation=generation,
            id=id,
            profile_id=profile_id,
            progress_percent=progress_percent,
            retry_not_before=retry_not_before,
            retry_request_count=retry_request_count,
            stage=stage,
            started_at=started_at,
            status=status,
            updated_at=updated_at,
        )

        document_job_info.additional_properties = d
        return document_job_info

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
