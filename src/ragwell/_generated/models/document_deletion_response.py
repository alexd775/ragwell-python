from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_deletion_state import DocumentDeletionState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.command_acceptance import CommandAcceptance


T = TypeVar("T", bound="DocumentDeletionResponse")


@_attrs_define
class DocumentDeletionResponse:
    analysis_artifact_count: int
    attempt_count: int
    attempt_record_count: int
    chunk_count: int
    chunk_part_count: int
    completed_at: datetime.datetime | None
    deleted_object_count: int
    document_id: UUID
    error_code: None | str
    generation_count: int
    id: UUID
    job_count: int
    object_count: int
    outbox_count: int
    page_count: int
    requested_at: datetime.datetime
    retry_request_count: int
    source_count: int
    state: DocumentDeletionState
    updated_at: datetime.datetime
    vector_count: int
    version_count: int
    command: CommandAcceptance | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.command_acceptance import CommandAcceptance

        analysis_artifact_count = self.analysis_artifact_count

        attempt_count = self.attempt_count

        attempt_record_count = self.attempt_record_count

        chunk_count = self.chunk_count

        chunk_part_count = self.chunk_part_count

        completed_at: None | str
        if isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        deleted_object_count = self.deleted_object_count

        document_id = str(self.document_id)

        error_code: None | str
        error_code = self.error_code

        generation_count = self.generation_count

        id = str(self.id)

        job_count = self.job_count

        object_count = self.object_count

        outbox_count = self.outbox_count

        page_count = self.page_count

        requested_at = self.requested_at.isoformat()

        retry_request_count = self.retry_request_count

        source_count = self.source_count

        state = self.state.value

        updated_at = self.updated_at.isoformat()

        vector_count = self.vector_count

        version_count = self.version_count

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
                "analysis_artifact_count": analysis_artifact_count,
                "attempt_count": attempt_count,
                "attempt_record_count": attempt_record_count,
                "chunk_count": chunk_count,
                "chunk_part_count": chunk_part_count,
                "completed_at": completed_at,
                "deleted_object_count": deleted_object_count,
                "document_id": document_id,
                "error_code": error_code,
                "generation_count": generation_count,
                "id": id,
                "job_count": job_count,
                "object_count": object_count,
                "outbox_count": outbox_count,
                "page_count": page_count,
                "requested_at": requested_at,
                "retry_request_count": retry_request_count,
                "source_count": source_count,
                "state": state,
                "updated_at": updated_at,
                "vector_count": vector_count,
                "version_count": version_count,
            }
        )
        if command is not UNSET:
            field_dict["command"] = command

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.command_acceptance import CommandAcceptance

        d = dict(src_dict)
        analysis_artifact_count = d.pop("analysis_artifact_count")

        attempt_count = d.pop("attempt_count")

        attempt_record_count = d.pop("attempt_record_count")

        chunk_count = d.pop("chunk_count")

        chunk_part_count = d.pop("chunk_part_count")

        def _parse_completed_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = datetime.datetime.fromisoformat(data)

                return completed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        completed_at = _parse_completed_at(d.pop("completed_at"))

        deleted_object_count = d.pop("deleted_object_count")

        document_id = UUID(d.pop("document_id"))

        def _parse_error_code(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error_code = _parse_error_code(d.pop("error_code"))

        generation_count = d.pop("generation_count")

        id = UUID(d.pop("id"))

        job_count = d.pop("job_count")

        object_count = d.pop("object_count")

        outbox_count = d.pop("outbox_count")

        page_count = d.pop("page_count")

        requested_at = datetime.datetime.fromisoformat(d.pop("requested_at"))

        retry_request_count = d.pop("retry_request_count")

        source_count = d.pop("source_count")

        state = DocumentDeletionState(d.pop("state"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        vector_count = d.pop("vector_count")

        version_count = d.pop("version_count")

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

        document_deletion_response = cls(
            analysis_artifact_count=analysis_artifact_count,
            attempt_count=attempt_count,
            attempt_record_count=attempt_record_count,
            chunk_count=chunk_count,
            chunk_part_count=chunk_part_count,
            completed_at=completed_at,
            deleted_object_count=deleted_object_count,
            document_id=document_id,
            error_code=error_code,
            generation_count=generation_count,
            id=id,
            job_count=job_count,
            object_count=object_count,
            outbox_count=outbox_count,
            page_count=page_count,
            requested_at=requested_at,
            retry_request_count=retry_request_count,
            source_count=source_count,
            state=state,
            updated_at=updated_at,
            vector_count=vector_count,
            version_count=version_count,
            command=command,
        )

        document_deletion_response.additional_properties = d
        return document_deletion_response

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
