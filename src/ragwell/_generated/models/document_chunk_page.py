from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_chunk_info import DocumentChunkInfo


T = TypeVar("T", bound="DocumentChunkPage")


@_attrs_define
class DocumentChunkPage:
    generation_id: UUID
    items: list[DocumentChunkInfo]
    matching_count: int
    next_cursor: int | None
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generation_id = str(self.generation_id)

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        matching_count = self.matching_count

        next_cursor: int | None
        next_cursor = self.next_cursor

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generation_id": generation_id,
                "items": items,
                "matching_count": matching_count,
                "next_cursor": next_cursor,
                "total_count": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_chunk_info import DocumentChunkInfo

        d = dict(src_dict)
        generation_id = UUID(d.pop("generation_id"))

        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = DocumentChunkInfo.from_dict(items_item_data)

            items.append(items_item)

        matching_count = d.pop("matching_count")

        def _parse_next_cursor(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor"))

        total_count = d.pop("total_count")

        document_chunk_page = cls(
            generation_id=generation_id,
            items=items,
            matching_count=matching_count,
            next_cursor=next_cursor,
            total_count=total_count,
        )

        document_chunk_page.additional_properties = d
        return document_chunk_page

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
