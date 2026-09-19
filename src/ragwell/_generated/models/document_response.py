from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_state import DocumentState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.command_acceptance import CommandAcceptance
    from ..models.document_metadata_response import DocumentMetadataResponse


T = TypeVar("T", bound="DocumentResponse")


@_attrs_define
class DocumentResponse:
    created_at: datetime.datetime
    id: UUID
    metadata: DocumentMetadataResponse
    metadata_revision: int
    metadata_updated_at: datetime.datetime
    original_filename: str
    state: DocumentState
    tags: list[str]
    updated_at: datetime.datetime
    command: CommandAcceptance | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.command_acceptance import CommandAcceptance

        created_at = self.created_at.isoformat()

        id = str(self.id)

        metadata = self.metadata.to_dict()

        metadata_revision = self.metadata_revision

        metadata_updated_at = self.metadata_updated_at.isoformat()

        original_filename = self.original_filename

        state = self.state.value

        tags = self.tags

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
                "created_at": created_at,
                "id": id,
                "metadata": metadata,
                "metadata_revision": metadata_revision,
                "metadata_updated_at": metadata_updated_at,
                "original_filename": original_filename,
                "state": state,
                "tags": tags,
                "updated_at": updated_at,
            }
        )
        if command is not UNSET:
            field_dict["command"] = command

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.command_acceptance import CommandAcceptance
        from ..models.document_metadata_response import DocumentMetadataResponse

        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        id = UUID(d.pop("id"))

        metadata = DocumentMetadataResponse.from_dict(d.pop("metadata"))

        metadata_revision = d.pop("metadata_revision")

        metadata_updated_at = datetime.datetime.fromisoformat(
            d.pop("metadata_updated_at")
        )

        original_filename = d.pop("original_filename")

        state = DocumentState(d.pop("state"))

        tags = cast(list[str], d.pop("tags"))

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

        document_response = cls(
            created_at=created_at,
            id=id,
            metadata=metadata,
            metadata_revision=metadata_revision,
            metadata_updated_at=metadata_updated_at,
            original_filename=original_filename,
            state=state,
            tags=tags,
            updated_at=updated_at,
            command=command,
        )

        document_response.additional_properties = d
        return document_response

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
