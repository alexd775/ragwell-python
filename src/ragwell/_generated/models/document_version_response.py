from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_version_state import DocumentVersionState

T = TypeVar("T", bound="DocumentVersionResponse")


@_attrs_define
class DocumentVersionResponse:
    byte_size: int
    created_at: datetime.datetime
    document_id: UUID
    id: UUID
    media_type: str
    sha256: str
    state: DocumentVersionState
    version_number: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        byte_size = self.byte_size

        created_at = self.created_at.isoformat()

        document_id = str(self.document_id)

        id = str(self.id)

        media_type = self.media_type

        sha256 = self.sha256

        state = self.state.value

        version_number = self.version_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "byte_size": byte_size,
                "created_at": created_at,
                "document_id": document_id,
                "id": id,
                "media_type": media_type,
                "sha256": sha256,
                "state": state,
                "version_number": version_number,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        byte_size = d.pop("byte_size")

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        document_id = UUID(d.pop("document_id"))

        id = UUID(d.pop("id"))

        media_type = d.pop("media_type")

        sha256 = d.pop("sha256")

        state = DocumentVersionState(d.pop("state"))

        version_number = d.pop("version_number")

        document_version_response = cls(
            byte_size=byte_size,
            created_at=created_at,
            document_id=document_id,
            id=id,
            media_type=media_type,
            sha256=sha256,
            state=state,
            version_number=version_number,
        )

        document_version_response.additional_properties = d
        return document_version_response

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
