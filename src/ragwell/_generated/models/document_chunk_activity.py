from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DocumentChunkActivity")


@_attrs_define
class DocumentChunkActivity:
    appearances: int
    chunk_id: UUID
    content: str
    ordinal: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        appearances = self.appearances

        chunk_id = str(self.chunk_id)

        content = self.content

        ordinal = self.ordinal

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "appearances": appearances,
                "chunk_id": chunk_id,
                "content": content,
                "ordinal": ordinal,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        appearances = d.pop("appearances")

        chunk_id = UUID(d.pop("chunk_id"))

        content = d.pop("content")

        ordinal = d.pop("ordinal")

        document_chunk_activity = cls(
            appearances=appearances,
            chunk_id=chunk_id,
            content=content,
            ordinal=ordinal,
        )

        document_chunk_activity.additional_properties = d
        return document_chunk_activity

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
