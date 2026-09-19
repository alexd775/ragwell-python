from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_export_response_state import DocumentExportResponseState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.command_acceptance import CommandAcceptance
    from ..models.document_export_part_response import DocumentExportPartResponse


T = TypeVar("T", bound="DocumentExportResponse")


@_attrs_define
class DocumentExportResponse:
    chunk_count: int
    completed_parts: int
    created_at: datetime.datetime
    document_version_id: UUID
    error_code: None | str
    expires_at: datetime.datetime
    failure_count: int
    generation_id: UUID
    id: UUID
    include_embeddings: bool
    parts: list[DocumentExportPartResponse]
    state: DocumentExportResponseState
    total_bytes: int
    total_parts: int
    command: CommandAcceptance | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.command_acceptance import CommandAcceptance

        chunk_count = self.chunk_count

        completed_parts = self.completed_parts

        created_at = self.created_at.isoformat()

        document_version_id = str(self.document_version_id)

        error_code: None | str
        error_code = self.error_code

        expires_at = self.expires_at.isoformat()

        failure_count = self.failure_count

        generation_id = str(self.generation_id)

        id = str(self.id)

        include_embeddings = self.include_embeddings

        parts = []
        for parts_item_data in self.parts:
            parts_item = parts_item_data.to_dict()
            parts.append(parts_item)

        state = self.state.value

        total_bytes = self.total_bytes

        total_parts = self.total_parts

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
                "chunk_count": chunk_count,
                "completed_parts": completed_parts,
                "created_at": created_at,
                "document_version_id": document_version_id,
                "error_code": error_code,
                "expires_at": expires_at,
                "failure_count": failure_count,
                "generation_id": generation_id,
                "id": id,
                "include_embeddings": include_embeddings,
                "parts": parts,
                "state": state,
                "total_bytes": total_bytes,
                "total_parts": total_parts,
            }
        )
        if command is not UNSET:
            field_dict["command"] = command

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.command_acceptance import CommandAcceptance
        from ..models.document_export_part_response import DocumentExportPartResponse

        d = dict(src_dict)
        chunk_count = d.pop("chunk_count")

        completed_parts = d.pop("completed_parts")

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        document_version_id = UUID(d.pop("document_version_id"))

        def _parse_error_code(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error_code = _parse_error_code(d.pop("error_code"))

        expires_at = datetime.datetime.fromisoformat(d.pop("expires_at"))

        failure_count = d.pop("failure_count")

        generation_id = UUID(d.pop("generation_id"))

        id = UUID(d.pop("id"))

        include_embeddings = d.pop("include_embeddings")

        parts = []
        _parts = d.pop("parts")
        for parts_item_data in _parts:
            parts_item = DocumentExportPartResponse.from_dict(parts_item_data)

            parts.append(parts_item)

        state = DocumentExportResponseState(d.pop("state"))

        total_bytes = d.pop("total_bytes")

        total_parts = d.pop("total_parts")

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

        document_export_response = cls(
            chunk_count=chunk_count,
            completed_parts=completed_parts,
            created_at=created_at,
            document_version_id=document_version_id,
            error_code=error_code,
            expires_at=expires_at,
            failure_count=failure_count,
            generation_id=generation_id,
            id=id,
            include_embeddings=include_embeddings,
            parts=parts,
            state=state,
            total_bytes=total_bytes,
            total_parts=total_parts,
            command=command,
        )

        document_export_response.additional_properties = d
        return document_export_response

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
